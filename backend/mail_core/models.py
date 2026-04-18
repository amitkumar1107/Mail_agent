from django.conf import settings
from django.db import models


class EmailDraft(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_READY = 'ready'
    STATUS_SENT = 'sent'
    STATUS_CANCELED = 'canceled'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_READY, 'Ready'),
        (STATUS_SENT, 'Sent'),
        (STATUS_CANCELED, 'Canceled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_drafts')
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=150, blank=True, default='')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    tone = models.CharField(max_length=40, blank=True, default='neutral')
    intent = models.CharField(max_length=80, blank=True, default='general')
    source_command = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status', 'created_at'], name='mail_core_e_user_id_42bd84_idx'),
        ]

    def __str__(self):
        return f'{self.recipient_email} - {self.subject}'


class SentEmailLog(models.Model):
    RESULT_SUCCESS = 'success'
    RESULT_FAILED = 'failed'

    RESULT_CHOICES = [
        (RESULT_SUCCESS, 'Success'),
        (RESULT_FAILED, 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_email_logs')
    draft = models.ForeignKey(EmailDraft, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_logs')
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    provider_message_id = models.CharField(max_length=255, blank=True, default='')
    error_message = models.TextField(blank=True, default='')
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['user', 'result', 'sent_at'], name='mail_core_s_user_id_eca1ea_idx'),
            models.Index(fields=['user', 'recipient_email'], name='mail_core_s_user_id_0ee7ba_idx'),
        ]


class CommandHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='command_history')
    command_text = models.TextField()
    parsed_intent = models.CharField(max_length=80, blank=True, default='general')
    parsed_tone = models.CharField(max_length=40, blank=True, default='neutral')
    parsed_occasion = models.CharField(max_length=80, blank=True, default='')
    parsed_action = models.CharField(max_length=40, blank=True, default='draft')
    parsed_schedule_time = models.CharField(max_length=120, blank=True, default='')
    detected_recipient = models.CharField(max_length=255, blank=True, default='')
    ai_used = models.BooleanField(default=False)
    ai_raw_output = models.TextField(blank=True, default='')
    ai_error = models.TextField(blank=True, default='')
    linked_draft = models.ForeignKey(EmailDraft, on_delete=models.SET_NULL, null=True, blank=True, related_name='commands')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at'], name='mail_core_c_user_id_03bebd_idx'),
            models.Index(fields=['user', 'parsed_intent', 'parsed_action'], name='mail_core_c_user_id_0c8bdb_idx'),
        ]
