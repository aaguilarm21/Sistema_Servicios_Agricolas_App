import json
import os
from io import StringIO
from unittest.mock import patch

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.management import call_command, CommandError
from django.test import Client
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.apps import apps
from datetime import date, timedelta
from decimal import Decimal

from .models import Empleado, FirmaAutorizada, Labor, LoginAttempt, RegistroOperativo, normalizar_texto
from .management.commands.createuserrole import Command as CreateUserRoleCommand
from .validators import PasswordStandardValidator
from .jwt_utils import generate_jwt_token, decode_jwt_token


class TimestampAuditFieldTests(TestCase):
    def test_every_accounts_model_has_creation_and_update_timestamps(self):
        for model in apps.get_app_config('accounts').get_models():
            with self.subTest(model=model.__name__):
                self.assertTrue(model._meta.get_field('created_at').auto_now_add)
                self.assertTrue(model._meta.get_field('updated_at').auto_now)

    def test_update_refreshes_timestamp_without_changing_creation_time(self):
        firma = FirmaAutorizada.objects.create(
            codigo='FIR-TIMESTAMP',
            nombre='Ana Lopez',
            puesto='Gerente',
            area='Operaciones',
        )
        created_at = firma.created_at
        self.assertGreaterEqual(firma.updated_at, created_at)
        previous_update = created_at - timedelta(days=1)
        FirmaAutorizada.objects.filter(pk=firma.pk).update(updated_at=previous_update)

        firma.refresh_from_db()
        firma.nombre = 'Ana Maria Lopez'
        firma.save()

        self.assertEqual(firma.created_at, created_at)
        self.assertGreater(firma.updated_at, previous_update)


class TextNormalizationOnSaveTests(TestCase):
    def test_text_is_normalized_on_create_and_update(self):
        self.assertEqual(normalizar_texto('it'), 'IT')
        self.assertEqual(normalizar_texto('IT'), 'IT')

        firma = FirmaAutorizada.objects.create(
            codigo='FIR-001',
            nombre='aNA lOPEZ',
            puesto='gERENTE it',
            area='oPERACIONES',
        )

        self.assertEqual(firma.nombre, 'Ana Lopez')
        self.assertEqual(firma.puesto, 'Gerente IT')
        self.assertEqual(firma.area, 'Operaciones')

        firma.nombre = 'mARÍA rUIZ'
        firma.save()

        self.assertEqual(firma.nombre, 'María Ruiz')


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


class GeneratedUserPasswordTests(TestCase):
    def test_generated_password_meets_password_policy(self):
        password = CreateUserRoleCommand().generate_temporary_password()

        PasswordStandardValidator().validate(password)
        self.assertGreaterEqual(len(password), 20)


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


class LoginAttemptTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='login-audit-user',
            password='TestPassword@123',
        )

    def test_successful_mobile_login_records_consented_gps_location(self):
        response = self.client.post(reverse('login'), {
            'username': 'login-audit-user',
            'password': 'TestPassword@123',
            'share_location': 'yes',
            'latitude': '14.634915',
            'longitude': '-90.506882',
            'location_status': 'captured',
        }, HTTP_USER_AGENT='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Mobile/15E148', REMOTE_ADDR='203.0.113.10')

        self.assertEqual(response.status_code, 302)
        attempt = LoginAttempt.objects.get(username_attempt='login-audit-user')
        self.assertTrue(attempt.successful)
        self.assertEqual(attempt.device_type, 'mobile')
        self.assertEqual(attempt.ip_address, '203.0.113.10')
        self.assertEqual(attempt.latitude, Decimal('14.634915'))
        self.assertEqual(attempt.longitude, Decimal('-90.506882'))
        self.assertEqual(attempt.location_status, 'captured')

    def test_failed_pc_login_records_attempt_without_location_consent(self):
        response = self.client.post(reverse('login'), {
            'username': 'login-audit-user',
            'password': 'WrongPassword@123',
        }, HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64)', REMOTE_ADDR='203.0.113.11')

        self.assertEqual(response.status_code, 200)
        attempt = LoginAttempt.objects.get(username_attempt='login-audit-user')
        self.assertFalse(attempt.successful)
        self.assertEqual(attempt.device_type, 'pc')
        self.assertEqual(attempt.ip_address, '203.0.113.11')
        self.assertIsNone(attempt.latitude)
        self.assertIsNone(attempt.longitude)
        self.assertEqual(attempt.location_status, 'not_shared')


class SignupAccessTests(TestCase):
    def test_anonymous_signup_redirects_to_login(self):
        response = self.client.get(reverse('signup'))

        self.assertRedirects(response, f'{reverse("login")}?next=%2Faccounts%2Fsignup%2F')

    def test_anonymous_signup_is_blocked_after_an_account_exists(self):
        User.objects.create_user(username='existing-user', password='TestPassword@123')
        user_count = User.objects.count()

        response = self.client.post(reverse('signup'), {})

        self.assertRedirects(response, f'{reverse("login")}?next=%2Faccounts%2Fsignup%2F')
        self.assertEqual(User.objects.count(), user_count)

    def test_regular_user_cannot_access_signup(self):
        user = User.objects.create_user(username='regular-user', password='TestPassword@123')
        self.client.force_login(user)
        self.client.cookies['jwt_token'] = generate_jwt_token(user)

        response = self.client.get(reverse('signup'))

        self.assertRedirects(response, reverse('modulos'))

    def test_admin_can_access_signup_after_initial_setup(self):
        admin = User.objects.create_superuser(
            username='admin-signup',
            email='admin-signup@example.com',
            password='TestPassword@123',
        )
        self.client.force_login(admin)
        self.client.cookies['jwt_token'] = generate_jwt_token(admin)

        response = self.client.get(reverse('signup'))

        self.assertEqual(response.status_code, 200)


class AdminProvisioningTests(TestCase):
    def test_migrations_do_not_change_existing_admin_password(self):
        admin = User.objects.create_superuser(
            username='stable-admin',
            email='stable-admin@example.com',
            password='Existing-Admin4!Pass',
        )
        original_hash = admin.password

        from .signals import ensure_default_groups
        ensure_default_groups(sender=apps.get_app_config('accounts'))

        admin.refresh_from_db()
        self.assertEqual(admin.password, original_hash)
        self.assertTrue(admin.check_password('Existing-Admin4!Pass'))

    def test_ensureadmin_requires_private_credentials(self):
        with patch.dict(os.environ, {
            'DJANGO_ADMIN_USERNAME': '',
            'DJANGO_ADMIN_PASSWORD': '',
        }):
            with self.assertRaises(CommandError):
                call_command('ensureadmin', stdout=StringIO(), stderr=StringIO())

        self.assertFalse(User.objects.filter(is_superuser=True).exists())

    def test_ensureadmin_preserves_existing_admin_without_credentials(self):
        admin = User.objects.create_superuser(
            username='kept-admin',
            email='kept-admin@example.com',
            password='Existing-Admin5!Pass',
        )
        original_hash = admin.password
        with patch.dict(os.environ, {
            'DJANGO_ADMIN_USERNAME': '',
            'DJANGO_ADMIN_PASSWORD': '',
        }):
            call_command('ensureadmin', stdout=StringIO())

        admin.refresh_from_db()
        self.assertEqual(admin.password, original_hash)

    def test_ensureadmin_creates_first_admin_from_environment(self):
        environment = {
            'DJANGO_ADMIN_USERNAME': 'first-admin',
            'DJANGO_ADMIN_EMAIL': 'first-admin@example.com',
            'DJANGO_ADMIN_PASSWORD': 'R8!mQ4#xV2$kP7',
        }
        with patch.dict(os.environ, environment):
            call_command('ensureadmin', stdout=StringIO())

        admin = User.objects.get(username='first-admin')
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.check_password(environment['DJANGO_ADMIN_PASSWORD']))

    def test_ensureadmin_rotates_only_the_named_existing_admin(self):
        admin = User.objects.create_superuser(
            username='maintainer-1',
            email='maintainer@example.com',
            password='Old-mN8!pQ4#vT2',
        )
        environment = {
            'DJANGO_ADMIN_USERNAME': 'maintainer-1',
            'DJANGO_ADMIN_EMAIL': 'maintainer@example.com',
            'DJANGO_ADMIN_PASSWORD': 'New-xC7@qR4!vP9',
        }
        with patch.dict(os.environ, environment):
            call_command('ensureadmin', stdout=StringIO())

        admin.refresh_from_db()
        self.assertTrue(admin.check_password(environment['DJANGO_ADMIN_PASSWORD']))
        self.assertFalse(admin.check_password('Old-mN8!pQ4#vT2'))
        self.assertEqual(User.objects.filter(is_superuser=True).count(), 1)


class AjaxLoginSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='ajax-security-user',
            password='Ajax-Secure4!Password',
        )
        self.client = Client(enforce_csrf_checks=True)

    def test_ajax_login_rejects_request_without_csrf_token(self):
        response = self.client.post(
            reverse('ajax_login'),
            data=json.dumps({'username': self.user.username, 'password': 'Ajax-Secure4!Password'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)

    def test_ajax_login_does_not_accept_credentials_in_get_parameters(self):
        response = self.client.get(reverse('ajax_login'), {
            'username': self.user.username,
            'password': 'Ajax-Secure4!Password',
        })

        self.assertEqual(response.status_code, 405)

    @override_settings(SESSION_COOKIE_SECURE=True)
    def test_ajax_login_accepts_csrf_header_and_sets_secure_jwt_cookie(self):
        login_page = self.client.get(reverse('login'))
        csrf_token = login_page.cookies['csrftoken'].value

        response = self.client.post(
            reverse('ajax_login'),
            data=json.dumps({'username': self.user.username, 'password': 'Ajax-Secure4!Password'}),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertNotIn('token', response.json())
        self.assertTrue(response.cookies['jwt_token']['httponly'])
        self.assertTrue(response.cookies['jwt_token']['secure'])


class DeviceDetectionTests(TestCase):
    def test_mobile_user_agent_is_exposed_to_templates(self):
        response = self.client.get(
            reverse('login'),
            HTTP_USER_AGENT='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Mobile/15E148',
        )

        self.assertContains(response, 'data-device-type="mobile"')
        self.assertContains(response, 'data-mobile-device="true"')
        self.assertIn('User-Agent', response.headers['Vary'])

    def test_pc_user_agent_is_exposed_to_templates(self):
        response = self.client.get(
            reverse('login'),
            HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        )

        self.assertContains(response, 'data-device-type="pc"')
        self.assertContains(response, 'data-mobile-device="false"')


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


class FirmaAutorizadaTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin-firmas',
            email='admin-firmas@example.com',
            password='TestPassword@123',
        )
        self.client.force_login(self.admin)
        self.client.cookies['jwt_token'] = generate_jwt_token(self.admin)
        Empleado.objects.create(
            empresa='Operaciones',
            empleado='Ana',
            segundo_apellido='Lopez',
            no_cui='1234567890123',
            puesto='FIR-001',
            nombre_puesto='Gerente Agricola',
        )

    def test_admin_can_register_authorized_signature(self):
        response = self.client.post('/firmas-autorizadas/', {
            'codigo': 'FIR-001',
        })

        self.assertRedirects(response, '/firmas-autorizadas/')
        firma = FirmaAutorizada.objects.get(codigo='FIR-001')
        self.assertEqual(firma.nombre, 'Ana Lopez')
        self.assertEqual(firma.puesto, 'Gerente Agricola')
        self.assertEqual(firma.area, 'Operaciones')

    def test_employee_lookup_returns_area_from_company(self):
        response = self.client.get('/accounts/api/buscar-usuario/?codigo=FIR-001')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['area'], 'Operaciones')

    def test_duplicate_code_is_rejected_without_creating_another_record(self):
        FirmaAutorizada.objects.create(
            codigo='FIR-001',
            nombre='Ana Lopez',
            puesto='Gerente Agricola',
            area='Administracion',
        )

        response = self.client.post('/firmas-autorizadas/', {
            'codigo': 'fir-001',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(FirmaAutorizada.objects.count(), 1)
        self.assertContains(response, 'Ya existe una firma autorizada con ese código.')


class EmployeeDataPrivacyTests(TestCase):
    def setUp(self):
        Empleado.objects.create(
            empresa='Operaciones',
            empleado='Persona de Prueba',
            segundo_apellido='Apellido',
            no_cui='1234567890123',
            puesto='PRIV-001',
            nombre_puesto='Operador',
        )

    def test_regular_user_does_not_receive_employee_cui(self):
        user = User.objects.create_user(username='employee-data-user', password='Valid-User4!Pass')
        self.client.force_login(user)
        self.client.cookies['jwt_token'] = generate_jwt_token(user)

        response = self.client.get(reverse('api_empleados'))

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('no_cui', response.json()[0])

    def test_admin_can_view_employee_cui_in_catalog(self):
        admin = User.objects.create_superuser(
            username='employee-data-admin',
            email='employee-data-admin@example.com',
            password='Valid-Admin4!Pass',
        )
        self.client.force_login(admin)
        self.client.cookies['jwt_token'] = generate_jwt_token(admin)

        response = self.client.get(reverse('api_empleados'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['no_cui'], '1234567890123')


class IndicadoresTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin-indicadores',
            email='admin-indicadores@example.com',
            password='TestPassword@123',
        )
        self.client.force_login(self.admin)
        self.client.cookies['jwt_token'] = generate_jwt_token(self.admin)

    def test_indicators_aggregate_operational_records(self):
        RegistroOperativo.objects.create(
            no_boleta='B-IND-001',
            fecha_labor=date(2026, 9, 1),
            tipo_servicio='Preparacion de suelo',
            proveedor='Proveedor',
            finca='Finca Norte',
            lote='Lote 1',
            area_lote=Decimal('2.50'),
            unidades=Decimal('4.00'),
            costo_unitario=Decimal('3.25'),
        )

        response = self.client.get('/indicadores/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_registros'], 1)
        self.assertEqual(response.context['area_total'], Decimal('2.50'))
        self.assertEqual(response.context['unidades_totales'], Decimal('4.00'))
        self.assertEqual(response.context['costo_calculado'], Decimal('13.00'))


class ValidarRegistroOperativoTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='usuario-validacion',
            password='TestPassword@123',
        )
        self.client.force_login(self.user)
        self.client.cookies['jwt_token'] = generate_jwt_token(self.user)

    def crear_registro(self, proveedor):
        return RegistroOperativo.objects.create(
            no_boleta='BOLETA-5420',
            fecha_labor=date(2026, 9, 20),
            tipo_servicio='Aplicaciones aereas',
            proveedor=proveedor,
            finca='Finca Central',
            lote='Lote 8',
            area_lote=Decimal('12.50'),
            operador='Carlos Ruiz',
            observaciones='Registro de prueba',
        )

    def test_search_displays_all_details_for_boleta_number(self):
        self.crear_registro('Proveedor Central')
        self.crear_registro('Proveedor Alterno')

        response = self.client.get(reverse('validar_registro_operativo'), {
            'no_boleta': 'boleta-5420',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['registros'].count(), 2)
        self.assertContains(response, 'Finca Central')
        self.assertContains(response, 'Carlos Ruiz')
        self.assertContains(response, 'Proveedor Central')
        self.assertContains(response, 'Proveedor Alterno')

    def test_search_shows_message_when_boleta_does_not_exist(self):
        response = self.client.get(reverse('validar_registro_operativo'), {
            'no_boleta': 'NO-EXISTE',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No se encontró una boleta')


class EditarRegistroOperativoTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin-editar-registro',
            email='admin-editar-registro@example.com',
            password='TestPassword@123',
        )
        self.client.force_login(self.admin)
        self.client.cookies['jwt_token'] = generate_jwt_token(self.admin)
        self.registro = RegistroOperativo.objects.create(
            no_boleta='BOLETA-EDITAR-1',
            fecha_labor=date(2026, 9, 20),
            tipo_servicio='Aplicaciones aereas',
            proveedor='Proveedor Central',
            placa='P-123ABC',
            finca='Finca Central',
            lote='Lote 8',
            area_lote=Decimal('12.50'),
            cuenta_contable='CTA-100',
        )

    def test_create_and_edit_pages_receive_the_same_catalogs(self):
        labor = Labor.objects.create(codigo='LAB-001', descripcion='Riego')

        create_response = self.client.get(reverse('registros'))
        edit_response = self.client.get(reverse('editar_registro', args=[self.registro.id]))

        catalog_names = (
            'proveedores', 'maquinarias', 'fincas', 'labores', 'variedades', 'municipios',
        )
        for catalog_name in catalog_names:
            with self.subTest(catalog=catalog_name):
                self.assertEqual(create_response.status_code, 200)
                self.assertEqual(edit_response.status_code, 200)
                self.assertEqual(
                    list(create_response.context[catalog_name]),
                    list(edit_response.context[catalog_name]),
                )

        self.assertEqual(list(create_response.context['labores']), [labor])

    def test_locked_fields_are_not_changed_by_edit_post(self):
        self.client.post(reverse('editar_registro', args=[self.registro.id]), {
            'placa': 'P-999XYZ',
            'area_lote': '99.99',
            'cuenta_contable': 'CTA-999',
            'lote': 'Lote actualizado',
        })

        self.registro.refresh_from_db()
        self.assertEqual(self.registro.placa, 'P-123ABC')
        self.assertEqual(self.registro.area_lote, Decimal('12.50'))
        self.assertEqual(self.registro.cuenta_contable, 'CTA-100')
        self.assertEqual(self.registro.lote, 'Lote Actualizado')
