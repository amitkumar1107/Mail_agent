from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from contacts.models import Contact

from .ai import generate_email, infer_command
from .email_providers import send_email_with_provider
from .models import CommandHistory, EmailDraft, SentEmailLog
from .tasks import send_draft_email_task
from .serializers import (
    CommandHistorySerializer,
    CommandParseSerializer,
    DraftConfirmSerializer,
    DraftPreviewSerializer,
    EmailDraftSerializer,
    PreviousEditSerializer,
    SentEmailLogSerializer,
    contact_to_candidate,
    find_contact_by_id_for_user,
    find_contacts_smart,
)


def _rule_fallback_intent_tone(command_text: str):
    text = (command_text or '').lower()

    if 'birthday' in text or 'wish' in text:
        intent = 'birthday_wish'
        occasion = 'birthday'
    elif 'apology' in text or 'sorry' in text:
        intent = 'apology'
        occasion = 'apology'
    elif 'remind' in text or 'meeting' in text:
        intent = 'reminder'
        occasion = 'meeting'
    else:
        intent = 'general'
        occasion = ''

    if 'formal' in text or 'sir' in text or 'madam' in text or 'boss' in text:
        tone = 'formal'
    elif 'friend' in text or 'bro' in text or 'yaar' in text or 'bhai' in text:
        tone = 'friendly'
    else:
        tone = 'neutral'

    return {
        'intent': intent,
        'tone': tone,
        'occasion': occasion,
        'action': 'draft',
        'schedule_time': '',
        'recipient_name': '',
        'language': '',
        'commands': [command_text] if command_text else [],
        'ai_used': False,
        'confidence': 0.4,
        'ai_raw_output': '',
        'ai_error': 'Fallback heuristic used',
    }


def _fallback_subject_body(intent: str, tone: str, recipient_name: str, command_text: str):
    name = recipient_name or 'there'

    if intent == 'birthday_wish':
        subject = f'Happy Birthday, {name}!'
        body = f'Dear {name},\n\nWishing you a very happy birthday and a wonderful year ahead.\n\nBest regards'
    elif intent == 'apology':
        subject = 'Sincere Apology'
        body = f'Dear {name},\n\nI sincerely apologize for the inconvenience. Thank you for your understanding.\n\nRegards'
    elif intent == 'reminder':
        subject = 'Friendly Reminder'
        body = f'Dear {name},\n\nThis is a reminder regarding our upcoming meeting.\n\nThanks'
    else:
        subject = 'Regarding your message'
        body = f'Dear {name},\n\n{command_text}\n\nRegards'

    if tone == 'friendly':
        body = body.replace('Dear', 'Hi').replace('Regards', 'Cheers')
    return subject, body


def _command_history_create(user, command_text: str, parsed: dict, recipient: str, linked_draft=None):
    return CommandHistory.objects.create(
        user=user,
        command_text=command_text,
        parsed_intent=parsed.get('intent', 'general'),
        parsed_tone=parsed.get('tone', 'neutral'),
        parsed_occasion=parsed.get('occasion', ''),
        parsed_action=parsed.get('action', 'draft'),
        parsed_schedule_time=parsed.get('schedule_time', ''),
        detected_recipient=recipient,
        ai_used=bool(parsed.get('ai_used', False)),
        ai_raw_output=parsed.get('ai_raw_output', ''),
        ai_error=parsed.get('ai_error', ''),
        linked_draft=linked_draft,
    )


def _resolve_contact(user, command_text: str, recipient_hint: str, explicit_contact_id=None):
    if explicit_contact_id:
        contact = find_contact_by_id_for_user(user, explicit_contact_id)
        if contact:
            return {
                'contact': contact,
                'recipient_name': contact.full_name,
                'recipient_email': contact.email,
                'candidates': [],
                'needs_disambiguation': False,
                'unknown_contact': False,
            }

    scored = find_contacts_smart(user, command_text, recipient_hint)

    if len(scored) == 1:
        contact = scored[0][0]
        return {
            'contact': contact,
            'recipient_name': contact.full_name,
            'recipient_email': contact.email,
            'candidates': [],
            'needs_disambiguation': False,
            'unknown_contact': False,
        }

    if len(scored) > 1:
        top_score = scored[0][1]
        second_score = scored[1][1]
        if top_score >= 1.6 and (top_score - second_score) >= 0.45:
            contact = scored[0][0]
            return {
                'contact': contact,
                'recipient_name': contact.full_name,
                'recipient_email': contact.email,
                'candidates': [contact_to_candidate(c, s) for c, s in scored[:3]],
                'needs_disambiguation': False,
                'unknown_contact': False,
            }

        candidates = [contact_to_candidate(c, s) for c, s in scored]
        return {
            'contact': None,
            'recipient_name': recipient_hint or '',
            'recipient_email': '',
            'candidates': candidates,
            'needs_disambiguation': True,
            'unknown_contact': False,
        }

    return {
        'contact': None,
        'recipient_name': recipient_hint or '',
        'recipient_email': '',
        'candidates': [],
        'needs_disambiguation': False,
        'unknown_contact': bool(recipient_hint),
    }




def _queue_draft_send(user, draft):
    draft.metadata = {**(draft.metadata or {}), 'send_queued_at': timezone.now().isoformat()}
    draft.save(update_fields=['metadata', 'updated_at'])
    async_result = send_draft_email_task.delay(draft.id, user.id)
    return {'task_id': getattr(async_result, 'id', '')}

def _send_draft_and_log(user, draft):
    result = send_email_with_provider(
        to_email=draft.recipient_email,
        subject=draft.subject,
        body=draft.body,
    )
    if not result.success:
        raise RuntimeError(result.error or 'Email provider failed')

    draft.status = EmailDraft.STATUS_SENT
    draft.save(update_fields=['status', 'updated_at'])

    sent_log = SentEmailLog.objects.create(
        user=user,
        draft=draft,
        recipient_email=draft.recipient_email,
        subject=draft.subject,
        body=draft.body,
        result=SentEmailLog.RESULT_SUCCESS,
        provider_message_id=f'{result.provider}:{result.message_id}',
    )
    return sent_log


class CommandParseAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CommandParseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        command_text = serializer.validated_data['command_text'].strip()
        parsed = infer_command(command_text)
        if not parsed.get('intent'):
            parsed = _rule_fallback_intent_tone(command_text)

        commands = parsed.get('commands') or []

        resolved = _resolve_contact(request.user, command_text, parsed.get('recipient_name', ''))

        metadata = {
            'needs_confirmation': True,
            'recipient_email': resolved['recipient_email'],
            'contact_id': resolved['contact'].id if resolved['contact'] else None,
            'needs_disambiguation': resolved['needs_disambiguation'],
            'candidates': resolved['candidates'],
            'unknown_contact': resolved['unknown_contact'],
            'commands': commands,
        }

        if resolved['unknown_contact']:
            metadata['create_contact_suggestion'] = {
                'full_name': resolved['recipient_name'],
                'note': 'Contact not found. Create this contact before sending.',
            }

        command_row = _command_history_create(request.user, command_text, parsed, resolved['recipient_name'])

        return Response(
            {
                'command_id': command_row.id,
                'intent': parsed.get('intent', 'general'),
                'tone': parsed.get('tone', 'neutral'),
                'occasion': parsed.get('occasion', ''),
                'action': parsed.get('action', 'draft'),
                'schedule_time': parsed.get('schedule_time', ''),
                'recipient_detected': resolved['recipient_name'],
                'metadata': metadata,
                'ai_used': parsed.get('ai_used', False),
                'ai_error': parsed.get('ai_error', ''),
                'confidence': parsed.get('confidence', 0.0),
            }
        )


class DraftPreviewAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = DraftPreviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        command_text = serializer.validated_data.get('command_text', '').strip()
        contact_id = serializer.validated_data.get('contact_id')

        intent = serializer.validated_data.get('intent', 'general')
        tone = serializer.validated_data.get('tone', 'neutral')
        occasion = serializer.validated_data.get('occasion', '')
        action = serializer.validated_data.get('action', 'draft')
        schedule_time = serializer.validated_data.get('schedule_time', '')

        recipient_name = serializer.validated_data.get('recipient_name', '').strip()
        recipient_email = serializer.validated_data.get('recipient_email') or ''

        parsed = {}
        effective_command = command_text
        if command_text:
            parsed = infer_command(command_text)
            if not parsed.get('intent'):
                parsed = _rule_fallback_intent_tone(command_text)

            commands = parsed.get('commands') or []
            if commands:
                effective_command = commands[0]

            intent = intent if intent != 'general' else parsed.get('intent', 'general')
            tone = tone if tone != 'neutral' else parsed.get('tone', 'neutral')
            occasion = occasion or parsed.get('occasion', '')
            action = action if action != 'draft' else parsed.get('action', 'draft')
            schedule_time = schedule_time or parsed.get('schedule_time', '')
            recipient_name = recipient_name or parsed.get('recipient_name', '')

        resolved = _resolve_contact(request.user, command_text, recipient_name, explicit_contact_id=contact_id)

        if resolved['needs_disambiguation'] and not recipient_email:
            return Response(
                {
                    'detail': 'Multiple contacts matched. Please choose contact_id.',
                    'needs_disambiguation': True,
                    'candidates': resolved['candidates'],
                },
                status=status.HTTP_409_CONFLICT,
            )

        contact = resolved['contact']
        recipient_name = recipient_name or resolved['recipient_name']
        recipient_email = recipient_email or resolved['recipient_email']

        if not recipient_email:
            return Response(
                {
                    'detail': 'Could not detect recipient email. Provide recipient_email or create contact.',
                    'unknown_contact': resolved['unknown_contact'],
                    'suggested_contact': {'full_name': recipient_name, 'relationship': 'other'},
                },
                status=400,
            )

        relationship = contact.relationship if contact else 'other'

        subject = serializer.validated_data.get('subject', '').strip()
        body = serializer.validated_data.get('body', '').strip()

        ai_generation = {}
        if not subject or not body:
            ai_generation = generate_email(
                command_text=effective_command,
                intent=intent,
                tone=tone,
                recipient_name=recipient_name,
                relationship=relationship,
            )
            if ai_generation.get('subject') and ai_generation.get('body'):
                subject = subject or ai_generation['subject']
                body = body or ai_generation['body']
            else:
                fallback_subject, fallback_body = _fallback_subject_body(intent, tone, recipient_name, effective_command)
                subject = subject or fallback_subject
                body = body or fallback_body

        draft = EmailDraft.objects.create(
            user=request.user,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            subject=subject,
            body=body,
            tone=tone,
            intent=intent,
            source_command=command_text,
            status=EmailDraft.STATUS_READY,
            metadata={
                'preview_generated_at': timezone.now().isoformat(),
                'occasion': occasion,
                'action': action,
                'schedule_time': schedule_time,
                'contact_id': contact.id if contact else None,
                'ai_infer': parsed,
                'ai_generation': ai_generation,
            },
        )

        _command_history_create(
            request.user,
            command_text or f'preview for {recipient_email}',
            {
                'intent': intent,
                'tone': tone,
                'occasion': occasion,
                'action': action,
                'schedule_time': schedule_time,
                'ai_used': bool(parsed.get('ai_used', False) or ai_generation.get('ai_used', False)),
                'ai_raw_output': '\n'.join(
                    item for item in [parsed.get('ai_raw_output', ''), ai_generation.get('ai_raw_output', '')] if item
                ),
                'ai_error': '\n'.join(
                    item for item in [parsed.get('ai_error', ''), ai_generation.get('ai_error', '')] if item
                ),
            },
            recipient_name or recipient_email,
            linked_draft=draft,
        )

        return Response(
            {
                'message': 'Draft preview generated. Confirm with send/edit/cancel.',
                'draft': EmailDraftSerializer(draft).data,
                'allowed_actions': ['send', 'edit', 'cancel'],
            },
            status=status.HTTP_201_CREATED,
        )


class DraftConfirmAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = DraftConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        draft_id = serializer.validated_data['draft_id']
        action = serializer.validated_data['action']

        draft = EmailDraft.objects.filter(id=draft_id, user=request.user).first()
        if draft is None:
            return Response({'detail': 'Draft not found.'}, status=status.HTTP_404_NOT_FOUND)

        if draft.status in (EmailDraft.STATUS_SENT, EmailDraft.STATUS_CANCELED):
            return Response({'detail': f'Draft already {draft.status}.'}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'cancel':
            draft.status = EmailDraft.STATUS_CANCELED
            draft.save(update_fields=['status', 'updated_at'])
            return Response({'message': 'Draft canceled.', 'draft': EmailDraftSerializer(draft).data})

        if action == 'edit':
            updated_fields = []
            if 'subject' in serializer.validated_data:
                draft.subject = serializer.validated_data['subject']
                updated_fields.append('subject')
            if 'body' in serializer.validated_data:
                draft.body = serializer.validated_data['body']
                updated_fields.append('body')
            if not updated_fields:
                return Response({'detail': 'Provide subject and/or body for edit action.'}, status=400)

            updated_fields.append('updated_at')
            draft.save(update_fields=updated_fields)
            return Response({'message': 'Draft updated.', 'draft': EmailDraftSerializer(draft).data})

        if action == 'send':
            if draft.status != EmailDraft.STATUS_READY:
                return Response({'detail': 'Draft is not ready for sending.'}, status=400)

            if settings.MAIL_SEND_ASYNC:
                try:
                    queued = _queue_draft_send(request.user, draft)
                    return Response(
                        {
                            'message': 'Email send queued.',
                            'draft': EmailDraftSerializer(draft).data,
                            'task': queued,
                        },
                        status=status.HTTP_202_ACCEPTED,
                    )
                except Exception:
                    # Fallback to sync send if queueing fails.
                    pass

            try:
                sent_log = _send_draft_and_log(request.user, draft)
                return Response(
                    {
                        'message': 'Email sent successfully.',
                        'draft': EmailDraftSerializer(draft).data,
                        'sent_log': SentEmailLogSerializer(sent_log).data,
                    }
                )
            except Exception as exc:
                sent_log = SentEmailLog.objects.create(
                    user=request.user,
                    draft=draft,
                    recipient_email=draft.recipient_email,
                    subject=draft.subject,
                    body=draft.body,
                    result=SentEmailLog.RESULT_FAILED,
                    error_message=str(exc),
                )
                return Response(
                    {'detail': 'Failed to send email.', 'sent_log': SentEmailLogSerializer(sent_log).data},
                    status=500,
                )

        return Response({'detail': 'Unsupported action.'}, status=400)


class ResendLastMailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        last_success = SentEmailLog.objects.filter(
            user=request.user,
            result=SentEmailLog.RESULT_SUCCESS,
        ).order_by('-sent_at').first()
        if last_success is None:
            return Response({'detail': 'No previously sent mail found.'}, status=404)

        draft = EmailDraft.objects.create(
            user=request.user,
            recipient_email=last_success.recipient_email,
            recipient_name='',
            subject=last_success.subject,
            body=last_success.body,
            tone='neutral',
            intent='resend',
            source_command='resend last mail',
            status=EmailDraft.STATUS_READY,
            metadata={'resend_of_sent_log_id': last_success.id},
        )

        if settings.MAIL_SEND_ASYNC:
            try:
                queued = _queue_draft_send(request.user, draft)
                return Response({'message': 'Resend queued.', 'task': queued}, status=status.HTTP_202_ACCEPTED)
            except Exception:
                pass

        try:
            sent_log = _send_draft_and_log(request.user, draft)
            return Response({'message': 'Last email resent.', 'sent_log': SentEmailLogSerializer(sent_log).data})
        except Exception as exc:
            failed_log = SentEmailLog.objects.create(
                user=request.user,
                draft=draft,
                recipient_email=draft.recipient_email,
                subject=draft.subject,
                body=draft.body,
                result=SentEmailLog.RESULT_FAILED,
                error_message=str(exc),
            )
            return Response({'detail': 'Resend failed.', 'sent_log': SentEmailLogSerializer(failed_log).data}, status=500)


class EditPreviousMessageAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PreviousEditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        draft_id = serializer.validated_data.get('draft_id')
        if draft_id:
            draft = EmailDraft.objects.filter(id=draft_id, user=request.user).first()
        else:
            draft = EmailDraft.objects.filter(user=request.user).exclude(status=EmailDraft.STATUS_CANCELED).order_by('-updated_at').first()

        if draft is None:
            return Response({'detail': 'No draft found to edit.'}, status=404)

        updated = []
        if 'subject' in serializer.validated_data:
            draft.subject = serializer.validated_data['subject']
            updated.append('subject')
        if 'body' in serializer.validated_data:
            draft.body = serializer.validated_data['body']
            updated.append('body')
        if not updated:
            return Response({'detail': 'Provide subject and/or body.'}, status=400)

        updated.append('updated_at')
        draft.save(update_fields=updated)
        return Response({'message': 'Previous message updated.', 'draft': EmailDraftSerializer(draft).data})


class DraftListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        drafts = EmailDraft.objects.filter(user=request.user)
        status_filter = request.query_params.get('status', '').strip()
        if status_filter:
            drafts = drafts.filter(status=status_filter)
        return Response({'results': EmailDraftSerializer(drafts, many=True).data})


class SentMailHistoryAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        logs = SentEmailLog.objects.filter(user=request.user)
        recipient = request.query_params.get('recipient', '').strip()
        if recipient:
            logs = logs.filter(recipient_email__icontains=recipient)
        result = request.query_params.get('result', '').strip()
        if result:
            logs = logs.filter(result=result)
        return Response({'results': SentEmailLogSerializer(logs, many=True).data})


class CommandHistoryAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        rows = CommandHistory.objects.filter(user=request.user)
        intent = request.query_params.get('intent', '').strip()
        if intent:
            rows = rows.filter(parsed_intent=intent)
        action = request.query_params.get('action', '').strip()
        if action:
            rows = rows.filter(parsed_action=action)
        return Response({'results': CommandHistorySerializer(rows, many=True).data})


class DashboardInsightsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        cache_key = f'dashboard_insights:{user.id}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        today = timezone.localdate()
        next_30 = today + timedelta(days=30)

        sent_qs = SentEmailLog.objects.filter(user=user)
        reminders_count = user.reminders.filter(status='pending').count()
        sent_count = sent_qs.count()

        frequent = (
            sent_qs.values('recipient_email')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        user_contacts = list(Contact.objects.filter(user=user).only('id', 'full_name', 'email', 'birth_date', 'anniversary_date'))

        contact_map = {
            (c.email or '').lower(): c.full_name
            for c in user_contacts
            if c.email
        }

        frequent_contacts = [
            {
                'recipient_email': row['recipient_email'],
                'recipient_name': contact_map.get((row['recipient_email'] or '').lower(), ''),
                'count': row['count'],
            }
            for row in frequent
        ]

        upcoming_contacts = []
        for c in user_contacts:
            events = []
            if c.birth_date:
                events.append(('birthday', c.birth_date.month, c.birth_date.day))
            if c.anniversary_date:
                events.append(('anniversary', c.anniversary_date.month, c.anniversary_date.day))
            for event_type, m, d in events:
                try:
                    event_date = today.replace(month=m, day=d)
                except ValueError:
                    continue
                if event_date < today:
                    event_date = event_date.replace(year=today.year + 1)
                if today <= event_date <= next_30:
                    upcoming_contacts.append(
                        {
                            'contact_id': c.id,
                            'full_name': c.full_name,
                            'event_type': event_type,
                            'event_date': event_date.isoformat(),
                        }
                    )

        suggestions = []
        if upcoming_contacts:
            first = sorted(upcoming_contacts, key=lambda x: x['event_date'])[0]
            suggestions.append(f"{first['full_name']} has {first['event_type']} on {first['event_date']}.")
        if sent_count == 0:
            suggestions.append('Send your first email command to start personalized insights.')

        payload = {
            'sent_count': sent_count,
            'pending_reminders_count': reminders_count,
            'frequent_contacts': frequent_contacts,
            'upcoming_events': sorted(upcoming_contacts, key=lambda x: x['event_date'])[:10],
            'suggestions': suggestions,
        }
        cache.set(cache_key, payload, 120)
        return Response(payload)
