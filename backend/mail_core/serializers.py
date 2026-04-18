import hashlib
import json
from difflib import SequenceMatcher

from django.core.cache import cache
from django.db.models import Count, Max
from django.utils import timezone
from rest_framework import serializers

from contacts.models import Contact

from .models import CommandHistory, EmailDraft, SentEmailLog

ALLOWED_TONES = {'formal', 'casual', 'friendly', 'neutral'}
ALLOWED_ACTIONS = {'send', 'remind', 'draft'}
CONTACT_MATCH_CACHE_TTL = 120


class CommandParseSerializer(serializers.Serializer):
    command_text = serializers.CharField()


class DraftPreviewSerializer(serializers.Serializer):
    command_text = serializers.CharField(required=False, allow_blank=True)
    contact_id = serializers.IntegerField(required=False)
    recipient_email = serializers.EmailField(required=False)
    recipient_name = serializers.CharField(required=False, allow_blank=True)
    subject = serializers.CharField(required=False, allow_blank=True)
    body = serializers.CharField(required=False, allow_blank=True)
    tone = serializers.CharField(required=False, allow_blank=True, default='neutral')
    intent = serializers.CharField(required=False, allow_blank=True, default='general')
    occasion = serializers.CharField(required=False, allow_blank=True, default='')
    action = serializers.CharField(required=False, allow_blank=True, default='draft')
    schedule_time = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_tone(self, value):
        tone = (value or 'neutral').strip().lower()
        return tone if tone in ALLOWED_TONES else 'neutral'

    def validate_action(self, value):
        action = (value or 'draft').strip().lower()
        return action if action in ALLOWED_ACTIONS else 'draft'

    def validate(self, attrs):
        if not attrs.get('recipient_email') and not attrs.get('command_text') and not attrs.get('contact_id'):
            raise serializers.ValidationError(
                'Provide contact_id, recipient_email, or command_text for preview generation.'
            )
        return attrs


class DraftConfirmSerializer(serializers.Serializer):
    draft_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['send', 'edit', 'cancel'])
    subject = serializers.CharField(required=False, allow_blank=False)
    body = serializers.CharField(required=False, allow_blank=False)


class PreviousEditSerializer(serializers.Serializer):
    draft_id = serializers.IntegerField(required=False)
    subject = serializers.CharField(required=False, allow_blank=False)
    body = serializers.CharField(required=False, allow_blank=False)


class EmailDraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailDraft
        fields = (
            'id',
            'recipient_email',
            'recipient_name',
            'subject',
            'body',
            'tone',
            'intent',
            'source_command',
            'status',
            'metadata',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'status')


class SentEmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentEmailLog
        fields = (
            'id',
            'draft',
            'recipient_email',
            'subject',
            'body',
            'result',
            'provider_message_id',
            'error_message',
            'sent_at',
        )


class CommandHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CommandHistory
        fields = (
            'id',
            'command_text',
            'parsed_intent',
            'parsed_tone',
            'parsed_occasion',
            'parsed_action',
            'parsed_schedule_time',
            'detected_recipient',
            'ai_used',
            'ai_error',
            'linked_draft',
            'created_at',
        )


def _similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _build_contact_activity_maps(user):
    freq_map = {}
    recency_map = {}

    email_stats = (
        SentEmailLog.objects.filter(user=user, result=SentEmailLog.RESULT_SUCCESS)
        .values('recipient_email')
        .annotate(total=Count('id'), last_sent=Max('sent_at'))
    )
    for row in email_stats:
        email = (row.get('recipient_email') or '').strip().lower()
        if email:
            freq_map[email] = int(row.get('total') or 0)
            recency_map[email] = row.get('last_sent')

    return freq_map, recency_map


def _activity_score(contact: Contact, freq_map, recency_map) -> float:
    email = (contact.email or '').strip().lower()
    if not email:
        return 0.0

    score = 0.0
    total = freq_map.get(email, 0)
    if total:
        score += min(0.6, total * 0.08)

    last = recency_map.get(email)
    if last:
        days = (timezone.now() - last).days
        if days <= 7:
            score += 0.5
        elif days <= 30:
            score += 0.3
        elif days <= 90:
            score += 0.15

    return score


def contact_to_candidate(contact: Contact, score: float):
    return {
        'id': contact.id,
        'full_name': contact.full_name,
        'email': contact.email,
        'relationship': contact.relationship,
        'score': round(score, 3),
    }


def find_contact_by_id_for_user(user, contact_id):
    return Contact.objects.filter(user=user, id=contact_id).first()


def _contact_match_cache_key(user_id: int, command_text: str, name_hint: str, limit: int) -> str:
    base = json.dumps(
        {
            'user_id': user_id,
            'command': (command_text or '').lower().strip(),
            'hint': (name_hint or '').lower().strip(),
            'limit': limit,
        },
        sort_keys=True,
    )
    digest = hashlib.sha256(base.encode('utf-8')).hexdigest()
    return f'contact_match:{digest}'


def find_contacts_smart(user, command_text: str, name_hint: str, limit: int = 5):
    cache_key = _contact_match_cache_key(user.id, command_text, name_hint, limit)
    cached = cache.get(cache_key)
    if cached is not None:
        contact_ids = [item['id'] for item in cached]
        contacts_map = {c.id: c for c in Contact.objects.filter(user=user, id__in=contact_ids)}
        resolved = []
        for item in cached:
            contact = contacts_map.get(item['id'])
            if contact:
                resolved.append((contact, float(item['score'])))
        return resolved

    contacts = Contact.objects.filter(user=user)
    command_lower = (command_text or '').lower()
    hint = (name_hint or '').strip()
    hint_lower = hint.lower()

    freq_map, recency_map = _build_contact_activity_maps(user)

    scored = []
    for contact in contacts:
        score = 0.0
        full = (contact.full_name or '').strip()
        full_lower = full.lower()

        if full and full_lower and full_lower in command_lower:
            score += 1.2

        if hint:
            if full_lower == hint_lower:
                score += 1.1
            elif hint_lower in full_lower:
                score += 0.85
            score += _similarity(full, hint) * 0.9

        if contact.relationship and contact.relationship in command_lower:
            score += 0.2

        if contact.email and contact.email.lower() in command_lower:
            score += 1.0
        if contact.phone and contact.phone in command_lower:
            score += 1.0

        score += _activity_score(contact, freq_map, recency_map)

        if score > 0:
            scored.append((contact, score))

    scored.sort(key=lambda item: item[1], reverse=True)
    scored = scored[:limit]

    cache_payload = [{'id': c.id, 'score': s} for c, s in scored]
    cache.set(cache_key, cache_payload, CONTACT_MATCH_CACHE_TTL)
    return scored
