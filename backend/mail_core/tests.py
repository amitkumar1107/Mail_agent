from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from contacts.models import Contact
from mail_core.models import EmailDraft, SentEmailLog


class _SendResult:
    def __init__(self, success=True, provider='test', message_id='1', error=''):
        self.success = success
        self.provider = provider
        self.message_id = message_id
        self.error = error


class MailCoreTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u2', password='Pass123456', email='u2@example.com', is_active=True)
        self.contact = Contact.objects.create(
            user=self.user,
            full_name='Amit Sharma',
            email='amit@example.com',
            phone='1234',
            relationship='friend',
        )
        token = str(RefreshToken.for_user(self.user).access_token)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    @patch('mail_core.views.infer_command')
    @patch('mail_core.views.generate_email')
    def test_preview_creates_draft(self, mock_generate, mock_infer):
        mock_infer.return_value = {
            'intent': 'birthday_wish',
            'tone': 'friendly',
            'occasion': 'birthday',
            'action': 'draft',
            'schedule_time': '',
            'recipient_name': 'Amit Sharma',
            'commands': ['Wish Amit happy birthday'],
            'ai_used': True,
            'confidence': 0.9,
            'ai_raw_output': '{}',
            'ai_error': '',
        }
        mock_generate.return_value = {
            'subject': 'Happy Birthday Amit',
            'body': 'Hi Amit, happy birthday!',
            'ai_used': True,
            'ai_raw_output': '{}',
            'ai_error': '',
        }
        resp = self.client.post('/api/mail/drafts/preview/', {'command_text': 'Wish Amit happy birthday'}, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(EmailDraft.objects.count(), 1)

    @patch('mail_core.views.send_email_with_provider')
    def test_confirm_send_marks_draft_sent(self, mock_send):
        mock_send.return_value = _SendResult(True, 'test', '42')
        draft = EmailDraft.objects.create(
            user=self.user,
            recipient_email='amit@example.com',
            recipient_name='Amit Sharma',
            subject='Hello',
            body='Body',
            tone='neutral',
            intent='general',
            status=EmailDraft.STATUS_READY,
        )
        resp = self.client.post('/api/mail/drafts/confirm/', {'draft_id': draft.id, 'action': 'send'}, format='json')
        self.assertEqual(resp.status_code, 200)
        draft.refresh_from_db()
        self.assertEqual(draft.status, EmailDraft.STATUS_SENT)
        self.assertEqual(SentEmailLog.objects.filter(user=self.user).count(), 1)

    @override_settings(MAIL_SEND_ASYNC=True)
    @patch('mail_core.views.send_draft_email_task')
    def test_confirm_send_queues_when_async_enabled(self, mock_task):
        class Result:
            id = 'task-1'

        mock_task.delay.return_value = Result()
        draft = EmailDraft.objects.create(
            user=self.user,
            recipient_email='amit@example.com',
            recipient_name='Amit Sharma',
            subject='Hello',
            body='Body',
            tone='neutral',
            intent='general',
            status=EmailDraft.STATUS_READY,
        )
        resp = self.client.post('/api/mail/drafts/confirm/', {'draft_id': draft.id, 'action': 'send'}, format='json')
        self.assertEqual(resp.status_code, 202)
        mock_task.delay.assert_called_once()

    @patch('mail_core.views.send_email_with_provider')
    def test_resend_last_mail_endpoint(self, mock_send):
        mock_send.return_value = _SendResult(True, 'test', '99')
        SentEmailLog.objects.create(
            user=self.user,
            recipient_email='amit@example.com',
            subject='Old',
            body='Old body',
            result=SentEmailLog.RESULT_SUCCESS,
        )
        resp = self.client.post('/api/mail/actions/resend-last/', {}, format='json')
        self.assertEqual(resp.status_code, 200)

    @patch('mail_core.views.infer_command')
    def test_parse_returns_disambiguation_candidates(self, mock_infer):
        Contact.objects.create(
            user=self.user,
            full_name='Amit Verma',
            email='amit.verma@example.com',
            phone='9988',
            relationship='work',
        )
        mock_infer.return_value = {
            'intent': 'birthday_wish',
            'tone': 'friendly',
            'occasion': 'birthday',
            'action': 'draft',
            'schedule_time': '',
            'recipient_name': 'Amit',
            'commands': ['Wish Amit happy birthday', 'Remind Rahul tomorrow'],
            'ai_used': True,
            'confidence': 0.92,
            'ai_raw_output': '{}',
            'ai_error': '',
        }

        resp = self.client.post('/api/mail/commands/parse/', {'command_text': 'Wish Amit happy birthday and then remind Rahul tomorrow'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data['metadata']['needs_disambiguation'])
        self.assertGreaterEqual(len(resp.data['metadata']['candidates']), 2)
        self.assertEqual(len(resp.data['metadata']['commands']), 2)

    @patch('mail_core.views.infer_command')
    def test_preview_requires_contact_when_ambiguous(self, mock_infer):
        Contact.objects.create(
            user=self.user,
            full_name='Amit Verma',
            email='amit.verma@example.com',
            phone='9988',
            relationship='work',
        )
        mock_infer.return_value = {
            'intent': 'general',
            'tone': 'neutral',
            'occasion': '',
            'action': 'draft',
            'schedule_time': '',
            'recipient_name': 'Amit',
            'commands': ['Email Amit about meeting'],
            'ai_used': True,
            'confidence': 0.6,
            'ai_raw_output': '{}',
            'ai_error': '',
        }

        resp = self.client.post('/api/mail/drafts/preview/', {'command_text': 'Email Amit about meeting'}, format='json')
        self.assertEqual(resp.status_code, 409)
        self.assertTrue(resp.data.get('needs_disambiguation'))
