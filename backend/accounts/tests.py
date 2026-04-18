from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import EmailOTP


class AuthFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_signup_creates_inactive_user_and_otp(self):
        resp = self.client.post(
            '/api/auth/signup/',
            {'username': 'amit', 'email': 'amit@example.com', 'password': 'StrongPass123!'},
            format='json',
        )
        self.assertEqual(resp.status_code, 201)
        user = User.objects.get(username='amit')
        self.assertFalse(user.is_active)
        self.assertTrue(EmailOTP.objects.filter(user=user, is_used=False).exists())

    def test_verify_otp_then_login_returns_tokens(self):
        self.client.post(
            '/api/auth/signup/',
            {'username': 'ravi', 'email': 'ravi@example.com', 'password': 'StrongPass123!'},
            format='json',
        )
        otp = EmailOTP.objects.filter(user__username='ravi').latest('created_at')

        verify = self.client.post(
            '/api/auth/otp/verify/',
            {'email': 'ravi@example.com', 'code': otp.code},
            format='json',
        )
        self.assertEqual(verify.status_code, 200)

        login = self.client.post(
            '/api/auth/login/',
            {'username': 'ravi', 'password': 'StrongPass123!'},
            format='json',
        )
        self.assertEqual(login.status_code, 200)
        self.assertIn('tokens', login.data)
        self.assertIn('access', login.data['tokens'])

    def test_request_otp_does_not_enumerate_users(self):
        User.objects.create_user(username='present', email='present@example.com', password='StrongPass123!', is_active=False)

        existing = self.client.post('/api/auth/otp/request/', {'email': 'present@example.com'}, format='json')
        missing = self.client.post('/api/auth/otp/request/', {'email': 'missing@example.com'}, format='json')

        self.assertEqual(existing.status_code, 200)
        self.assertEqual(missing.status_code, 200)
        self.assertEqual(existing.data.get('message'), missing.data.get('message'))
