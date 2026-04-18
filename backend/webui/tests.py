from django.test import TestCase


class HealthEndpointTests(TestCase):
    def test_health_live(self):
        resp = self.client.get('/health/live/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('status'), 'ok')

    def test_health_ready(self):
        resp = self.client.get('/health/ready/')
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertIn('checks', payload)
        self.assertTrue(payload['checks']['db'])
