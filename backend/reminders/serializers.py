from django.utils import timezone
from rest_framework import serializers

from .models import Reminder


class ReminderSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)

    class Meta:
        model = Reminder
        fields = (
            'id',
            'contact',
            'contact_name',
            'title',
            'message',
            'reminder_type',
            'scheduled_for',
            'auto_send_email',
            'status',
            'idempotency_key',
            'processed_at',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'status', 'processed_at', 'created_at', 'updated_at')

    def validate_contact(self, value):
        request = self.context['request']
        if value and value.user_id != request.user.id:
            raise serializers.ValidationError('Selected contact does not belong to current user.')
        return value

    def validate_scheduled_for(self, value):
        dt = value
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        return dt

    def validate_idempotency_key(self, value):
        return (value or '').strip()

    def validate(self, attrs):
        contact = attrs.get('contact')
        auto_send = attrs.get('auto_send_email', False)
        if auto_send and contact and not contact.email:
            raise serializers.ValidationError('Contact must have an email for auto_send_email reminders.')
        return attrs
