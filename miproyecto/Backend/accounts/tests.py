from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User

from .validators import PasswordStandardValidator
from .jwt_utils import generate_jwt_token, decode_jwt_token


class PasswordStandardValidatorTests(TestCase):
    def setUp(self):
        self.validator = PasswordStandardValidator()

    def test_valid_password(self):
        # Cumple min 8 caracteres, mayúscula, minúscula, número y carácter especial
        try:
            self.validator.validate("Agricola@2026")
        except ValidationError:
            self.fail("PasswordStandardValidator lanzó ValidationError para una contraseña válida.")

    def test_short_password(self):
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate("Ag1@")
        self.assertIn("al menos 8 caracteres", str(ctx.exception))

    def test_missing_upper(self):
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate("agricola@2026")
        self.assertIn("mayúscula", str(ctx.exception))

    def test_missing_lower(self):
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate("AGRICOLA@2026")
        self.assertIn("minúscula", str(ctx.exception))

    def test_missing_number(self):
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate("Agricola@Guatemala")
        self.assertIn("número", str(ctx.exception))

    def test_missing_special_character(self):
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate("Agricola2026")
        self.assertIn("carácter especial", str(ctx.exception))


class JWTTokenTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPassword@123',
            email='test@example.com'
        )

    def test_jwt_generation_and_decoding(self):
        token = generate_jwt_token(self.user)
        self.assertTrue(isinstance(token, str))

        payload = decode_jwt_token(token)
        self.assertEqual(payload['user_id'], self.user.id)
        self.assertEqual(payload['username'], 'testuser')

    def test_jwt_protected_route_without_token_redirects(self):
        # Acceder a /modulos/ sin cookie JWT debe redirigir a login
        response = self.client.get(reverse('modulos'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_jwt_protected_route_with_cookie_access_granted(self):
        token = generate_jwt_token(self.user)
        self.client.cookies['jwt_token'] = token
        response = self.client.get(reverse('modulos'))
        self.assertEqual(response.status_code, 200)


class LockoutTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username='testlockout',
            password='Password123@',
            email='lockout@example.com',
            is_active=True
        )

    @override_settings(LOGIN_RATE_LIMIT_ATTEMPTS=3, LOGIN_RATE_LIMIT_LOCKOUT_SECONDS=300)
    def test_lockout_after_3_failed_attempts(self):
        # Intentos 1 y 2
        for _ in range(2):
            res = self.client.post(reverse('login'), {
                'username': 'testlockout',
                'password': 'wrongpassword',
            })
            self.assertEqual(res.status_code, 200)

        # Intento 3: debe bloquear al usuario
        res3 = self.client.post(reverse('login'), {
            'username': 'testlockout',
            'password': 'wrongpassword',
        })
        self.assertEqual(res3.status_code, 200)
        content3 = res3.content.decode('utf-8')
        self.assertIn('bloqueado', content3.lower())

        # Verificar que el usuario fue desactivado en la base de datos
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
