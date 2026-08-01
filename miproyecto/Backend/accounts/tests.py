from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model


class LoginPageTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    @override_settings(LOGIN_RATE_LIMIT_ATTEMPTS=3, LOGIN_RATE_LIMIT_LOCKOUT_SECONDS=60)
    def test_login_blocks_after_repeated_failures(self):
        for _ in range(3):
            response = self.client.post(reverse('login'), {
                'username': 'unknownuser',
                'password': 'wrong-password',
            })
            self.assertEqual(response.status_code, 200)

        blocked_response = self.client.post(reverse('login'), {
            'username': 'unknownuser',
            'password': 'wrong-password',
        })

        content = blocked_response.content.decode('utf-8').lower()
        self.assertIn('demasiados intentos', content)

    def test_login_page_still_renders_when_form_has_errors(self):
        response = self.client.post(reverse('login'), {
            'username': '',
            'password': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Iniciar sesión')
