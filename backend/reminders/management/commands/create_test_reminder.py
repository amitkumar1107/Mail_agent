from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from reminders.models import Reminder
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create a test reminder for the first user'

    def handle(self, *args, **options):
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('No users found. Create a user first.'))
            return

        reminder = Reminder.objects.create(
            user=user,
            title='Test Reminder',
            message='This is a test reminder message.',
            scheduled_for=timezone.now() + timedelta(seconds=30),  # Due in 30 seconds
            auto_send_email=True,
        )
        self.stdout.write(
            self.style.SUCCESS(f'Created test reminder: {reminder.title} (ID: {reminder.id}) scheduled for {reminder.scheduled_for}')
        )