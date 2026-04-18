from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from contacts.models import Contact
from mail_core.models import EmailDraft, SentEmailLog

from .models import Reminder
from .tasks import create_daily_event_reminders, process_due_reminders


class _SendResult:
    def __init__(self, success=True, provider='test', message_id='1', error=''):
        self.success = success
        self.provider = provider
        self.message_id = message_id
        self.error = error


class ReminderTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u3', password='Pass123456', email='u3@example.com', is_active=True)
        self.contact = Contact.objects.create(
            user=self.user,
            full_name='Rahul Verma',
            email='rahul@example.com',
            relationship='friend',
            birth_date=timezone.localdate(),
        )

    @patch('reminders.tasks.send_email_with_provider')
    def test_process_due_reminders_marks_completed_and_sends(self, mock_send):
        mock_send.return_value = _SendResult(True, 'test', '44')
        reminder = Reminder.objects.create(
            user=self.user,
            contact=self.contact,
            title='Meeting reminder',
            message='Reminder message',
            reminder_type=Reminder.TYPE_CUSTOM,
            scheduled_for=timezone.now() - timedelta(minutes=1),
            auto_send_email=True,
            status=Reminder.STATUS_PENDING,
        )

        result = process_due_reminders()

        reminder.refresh_from_db()
        self.assertEqual(reminder.status, Reminder.STATUS_COMPLETED)
        self.assertEqual(result['count'], 1)
        self.assertEqual(SentEmailLog.objects.filter(user=self.user, result=SentEmailLog.RESULT_SUCCESS).count(), 1)

    @patch('reminders.tasks.send_email_with_provider')
    def test_process_due_reminders_skips_when_already_sent(self, mock_send):
        reminder = Reminder.objects.create(
            user=self.user,
            contact=self.contact,
            title='Already sent reminder',
            message='Message',
            reminder_type=Reminder.TYPE_CUSTOM,
            scheduled_for=timezone.now() - timedelta(minutes=1),
            auto_send_email=True,
            status=Reminder.STATUS_PENDING,
            idempotency_key='custom:already',
        )

        draft = EmailDraft.objects.create(
            user=self.user,
            recipient_email=self.contact.email,
            recipient_name=self.contact.full_name,
            subject='Already sent reminder',
            body='Message',
            tone='neutral',
            intent='reminder',
            source_command='manual',
            status=EmailDraft.STATUS_SENT,
            metadata={'reminder_id': reminder.id},
        )
        SentEmailLog.objects.create(
            user=self.user,
            draft=draft,
            recipient_email=self.contact.email,
            subject='Already sent reminder',
            body='Message',
            result=SentEmailLog.RESULT_SUCCESS,
        )

        result = process_due_reminders()

        reminder.refresh_from_db()
        self.assertEqual(reminder.status, Reminder.STATUS_COMPLETED)
        self.assertEqual(result['count'], 1)
        mock_send.assert_not_called()

    def test_create_daily_event_reminders_is_idempotent(self):
        first = create_daily_event_reminders()
        second = create_daily_event_reminders()

        self.assertGreaterEqual(first['created'], 1)
        self.assertEqual(second['created'], 0)
