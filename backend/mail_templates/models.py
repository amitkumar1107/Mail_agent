from django.conf import settings
from django.db import models


class EmailTemplate(models.Model):
    CATEGORY_BIRTHDAY = 'birthday'
    CATEGORY_THANK_YOU = 'thank_you'
    CATEGORY_APOLOGY = 'apology'
    CATEGORY_BUSINESS = 'business'
    CATEGORY_GENERAL = 'general'

    CATEGORY_CHOICES = [
        (CATEGORY_BIRTHDAY, 'Birthday'),
        (CATEGORY_THANK_YOU, 'Thank You'),
        (CATEGORY_APOLOGY, 'Apology'),
        (CATEGORY_BUSINESS, 'Business'),
        (CATEGORY_GENERAL, 'General'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_templates',
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default=CATEGORY_GENERAL)
    intent_key = models.CharField(max_length=80, blank=True, default='general')
    subject_template = models.CharField(max_length=255)
    body_template = models.TextField()
    is_system = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='uniq_template_name_per_user'),
        ]

    def __str__(self):
        scope = 'system' if self.is_system else f'user:{self.user_id}'
        return f'{scope}:{self.name}'
