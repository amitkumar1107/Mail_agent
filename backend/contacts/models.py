from django.conf import settings
from django.db import models


class ContactGroup(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contact_groups')
    name = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='uniq_group_per_user'),
        ]

    def __str__(self):
        return f'{self.user_id}:{self.name}'


class Contact(models.Model):
    RELATIONSHIP_FAMILY = 'family'
    RELATIONSHIP_FRIEND = 'friend'
    RELATIONSHIP_WORK = 'work'
    RELATIONSHIP_OTHER = 'other'

    RELATIONSHIP_CHOICES = [
        (RELATIONSHIP_FAMILY, 'Family'),
        (RELATIONSHIP_FRIEND, 'Friend'),
        (RELATIONSHIP_WORK, 'Work'),
        (RELATIONSHIP_OTHER, 'Other'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contacts')
    group = models.ForeignKey(ContactGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='contacts')
    full_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES, default=RELATIONSHIP_OTHER)
    birth_date = models.DateField(null=True, blank=True)
    anniversary_date = models.DateField(null=True, blank=True)
    tags = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['full_name']
        indexes = [
            models.Index(fields=['user', 'full_name']),
            models.Index(fields=['user', 'email']),
            models.Index(fields=['user', 'phone']),
        ]

    def __str__(self):
        return f'{self.full_name} ({self.user_id})'
