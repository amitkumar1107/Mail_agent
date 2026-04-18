import datetime

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from contacts.models import Contact
from mail_core.email_providers import send_email_with_provider
from mail_core.models import EmailDraft, SentEmailLog

from .models import Reminder


def _same_month_day(date_field, today):
    return date_field and date_field.month == today.month and date_field.day == today.day


@shared_task
def process_due_reminders():
    now = timezone.now()
    due = Reminder.objects.filter(
        status=Reminder.STATUS_PENDING,
        scheduled_for__lte=now,
    ).select_related('contact', 'user')[:100]

    processed_ids = []
    for reminder in due:
        with transaction.atomic():
            reminder = Reminder.objects.select_for_update().get(id=reminder.id)
            if reminder.status != Reminder.STATUS_PENDING:
                continue

            # Idempotency guard: skip if this reminder already produced a sent draft.
            already_sent = EmailDraft.objects.filter(
                user=reminder.user,
                status=EmailDraft.STATUS_SENT,
                metadata__reminder_id=reminder.id,
            ).exists()
            if already_sent:
                reminder.status = Reminder.STATUS_COMPLETED
                reminder.processed_at = timezone.now()
                reminder.save(update_fields=['status', 'processed_at', 'updated_at'])
                processed_ids.append(reminder.id)
                continue

            if reminder.auto_send_email and reminder.contact and reminder.contact.email:
                subject = reminder.title
                body = reminder.message or f'Reminder: {reminder.title}'

                draft = EmailDraft.objects.create(
                    user=reminder.user,
                    recipient_email=reminder.contact.email,
                    recipient_name=reminder.contact.full_name,
                    subject=subject,
                    body=body,
                    tone='neutral',
                    intent='reminder',
                    source_command=f'auto reminder:{reminder.id}',
                    status=EmailDraft.STATUS_READY,
                    metadata={'generated_by': 'reminder_task', 'reminder_id': reminder.id, 'idempotency_key': reminder.idempotency_key},
                )

                try:
                    result = send_email_with_provider(
                        to_email=reminder.contact.email,
                        subject=subject,
                        body=body,
                    )
                    if not result.success:
                        raise RuntimeError(result.error or 'Email provider failed')

                    draft.status = EmailDraft.STATUS_SENT
                    draft.save(update_fields=['status', 'updated_at'])
                    SentEmailLog.objects.create(
                        user=reminder.user,
                        draft=draft,
                        recipient_email=reminder.contact.email,
                        subject=subject,
                        body=body,
                        result=SentEmailLog.RESULT_SUCCESS,
                        provider_message_id=f'{result.provider}:{result.message_id}',
                    )
                except Exception as exc:
                    SentEmailLog.objects.create(
                        user=reminder.user,
                        draft=draft,
                        recipient_email=reminder.contact.email,
                        subject=subject,
                        body=body,
                        result=SentEmailLog.RESULT_FAILED,
                        error_message=str(exc),
                    )

            reminder.status = Reminder.STATUS_COMPLETED
            reminder.processed_at = timezone.now()
            reminder.save(update_fields=['status', 'processed_at', 'updated_at'])
            processed_ids.append(reminder.id)

    return {'processed_ids': processed_ids, 'count': len(processed_ids)}


@shared_task
def create_daily_event_reminders():
    today = timezone.localdate()
    local_tz = timezone.get_current_timezone()
    send_at_local = datetime.datetime.combine(today, datetime.time(hour=9, minute=0))
    send_at = timezone.make_aware(send_at_local, local_tz)

    contacts = Contact.objects.filter(user__isnull=False)
    created_count = 0

    for contact in contacts:
        user = contact.user
        if not user:
            continue

        events = []
        if _same_month_day(contact.birth_date, today):
            events.append(('birthday', f'Wish {contact.full_name} happy birthday'))
        if _same_month_day(contact.anniversary_date, today):
            events.append(('anniversary', f'Wish {contact.full_name} happy anniversary'))

        for event_type, title in events:
            key = f'{event_type}:{contact.id}:{today.isoformat()}'
            if Reminder.objects.filter(user=user, idempotency_key=key).exists():
                continue

            Reminder.objects.create(
                user=user,
                contact=contact,
                title=title,
                message=title,
                reminder_type=event_type,
                scheduled_for=send_at,
                auto_send_email=bool(contact.email),
                idempotency_key=key,
                status=Reminder.STATUS_PENDING,
            )
            created_count += 1

    return {'created': created_count}
