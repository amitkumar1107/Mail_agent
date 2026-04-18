from django.conf import settings
from django.db import models
from django.db.models import Q

from contacts.models import Contact


class Reminder(models.Model):
    TYPE_CUSTOM = 'custom'
    TYPE_BIRTHDAY = 'birthday'
    TYPE_ANNIVERSARY = 'anniversary'

    TYPE_CHOICES = [
        (TYPE_CUSTOM, 'Custom'),
        (TYPE_BIRTHDAY, 'Birthday'),
        (TYPE_ANNIVERSARY, 'Anniversary'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELED = 'canceled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELED, 'Canceled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reminders')
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name='reminders')
    title = models.CharField(max_length=150)
    message = models.TextField(blank=True, default='')
    reminder_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_CUSTOM)
    scheduled_for = models.DateTimeField()
    auto_send_email = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    idempotency_key = models.CharField(max_length=100, blank=True, default='')
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_for']
        indexes = [
            models.Index(fields=['user', 'scheduled_for']),
            models.Index(fields=['status', 'scheduled_for']),
            models.Index(fields=['idempotency_key']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'idempotency_key'],
                condition=~Q(idempotency_key=''),
                name='uniq_nonempty_reminder_idempotency_per_user',
            )
        ]

    def __str__(self):
        return f'{self.title} @ {self.scheduled_for}'
