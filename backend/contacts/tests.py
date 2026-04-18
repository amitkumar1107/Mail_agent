from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


class ContactApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u1', password='Pass123456', email='u1@example.com', is_active=True)
        token = str(RefreshToken.for_user(self.user).access_token)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_create_contact(self):
        resp = self.client.post(
            '/api/contacts/',
            {'full_name': 'Amit Sharma', 'email': 'amit@x.com', 'phone': '999', 'relationship': 'friend'},
            format='json',
        )
        self.assertEqual(resp.status_code, 201)

    def test_duplicate_contact_blocked(self):
        self.client.post(
            '/api/contacts/',
            {'full_name': 'Amit Sharma', 'email': 'amit@x.com', 'phone': '999', 'relationship': 'friend'},
            format='json',
        )
        resp = self.client.post(
            '/api/contacts/',
            {'full_name': 'Amit Verma', 'email': 'amit@x.com', 'phone': '888', 'relationship': 'work'},
            format='json',
        )
        self.assertEqual(resp.status_code, 400)
