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

from .models import (
    Articulo, Cuenta, DespachoCombustible, Empleado, FirmaAutorizada, Labor, LoginAttempt, Proveedor,
    Maquinaria, ProgramacionOperacion, RegistroOperativo, TanqueCombustible,
    normalizar_texto,
)
from .management.commands.createuserrole import Command as CreateUserRoleCommand
from .validators import PasswordStandardValidator
from .jwt_utils import generate_jwt_token, decode_jwt_token


class CuentaPorProcesoTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin-cuentas-proceso',
            email='admin-cuentas-proceso@example.com',
            password='TestPassword@123',
        )
        self.client.force_login(self.admin)
        self.client.cookies['jwt_token'] = generate_jwt_token(self.admin)
        Cuenta.objects.all().delete()

    def crear_cuenta(self, codigo, proceso, tipo='Gasto'):
        return self.client.post(
            reverse('api_cuentas'),
            data=json.dumps({
                'codigo': codigo,
                'descripcion': f'Cuenta {proceso}',
                'proceso': proceso,
                'tipo': tipo,
            }),
            content_type='application/json',
        )

    def test_solo_permite_una_cuenta_por_cada_proceso(self):
        for codigo, proceso in (
            ('522104100001', 'siembras'),
            ('522104100002', 'fertilizacion'),
            ('522104100003', 'riego'),
        ):
            with self.subTest(proceso=proceso):
                response = self.crear_cuenta(codigo, proceso)
                self.assertEqual(response.status_code, 201)

        respuesta_duplicada = self.crear_cuenta('522104100004', 'riego')

        self.assertEqual(respuesta_duplicada.status_code, 400)
        self.assertEqual(Cuenta.objects.count(), 3)

    def test_requiere_tipo_de_cuenta(self):
        response = self.crear_cuenta('522104100005', 'siembras', tipo='')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Cuenta.objects.count(), 0)

    def test_rechaza_codigos_que_no_tienen_exactamente_12_digitos(self):
        for codigo in ('5221041000095', '52210410001', '52210410000A'):
            with self.subTest(codigo=codigo):
                response = self.crear_cuenta(codigo, 'siembras')
                self.assertEqual(response.status_code, 400)

        self.assertEqual(Cuenta.objects.count(), 0)

    def test_rechaza_procesos_no_configurados(self):
        response = self.client.post(
            reverse('api_cuentas'),
            data=json.dumps({
                'codigo': '522104100006',
                'descripcion': 'Proceso no configurado',
                'proceso': 'administracion',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Cuenta.objects.count(), 0)


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

    def test_validation_shows_create_action_but_hides_admin_actions(self):
        self.crear_registro('Proveedor Central')
        response = self.client.get(reverse('validar_registro_operativo'), {
            'no_boleta': 'BOLETA-5420',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Crear registro')
        self.assertNotContains(response, 'Editar')
        self.assertNotContains(response, 'Eliminar')

    def test_admin_can_delete_a_record_with_post_only(self):
        registro = self.crear_registro('Proveedor Central')
        admin = User.objects.create_superuser(
            username='admin-validar-registro',
            email='admin-validar-registro@example.com',
            password='TestPassword@123',
        )
        self.client.force_login(admin)
        self.client.cookies['jwt_token'] = generate_jwt_token(admin)

        validation_response = self.client.get(reverse('validar_registro_operativo'), {
            'no_boleta': registro.no_boleta,
        })
        self.assertContains(validation_response, reverse('editar_registro', args=[registro.id]))
        self.assertContains(validation_response, reverse('borrar_registro', args=[registro.id]))

        get_response = self.client.get(reverse('borrar_registro', args=[registro.id]))
        self.assertEqual(get_response.status_code, 405)
        self.assertTrue(RegistroOperativo.objects.filter(pk=registro.pk).exists())

        post_response = self.client.post(reverse('borrar_registro', args=[registro.id]))
        self.assertRedirects(post_response, reverse('registros_data'))
        self.assertFalse(RegistroOperativo.objects.filter(pk=registro.pk).exists())


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

        self.assertIn(labor, list(create_response.context['labores']))

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


class LogisticaCrudTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin-logistica-crud',
            email='admin-logistica-crud@example.com',
            password='TestPassword@123',
        )
        self.client.force_login(self.admin)
        self.client.cookies['jwt_token'] = generate_jwt_token(self.admin)

    def test_operation_can_be_created_updated_and_deleted(self):
        datos = {
            'action': 'create',
            'tipo_servicio': 'Fertilización',
            'fecha': '2026-10-02',
            'finca': 'Finca Central',
            'lote': '0014',
            'area': '14.50',
            'responsable': 'Ana López',
            'prioridad': 'Normal',
            'estado': 'Programada',
            'observaciones': 'Aplicar según plan.',
        }
        create_response = self.client.post(reverse('operacion'), datos)

        self.assertRedirects(create_response, '/operacion/?ver=logistica')
        operacion = ProgramacionOperacion.objects.get()

        list_response = self.client.get(reverse('operacion'), {'ver': 'logistica'})
        self.assertContains(list_response, 'editarOperacion')
        self.assertContains(list_response, 'id="codigo_responsable"')

        datos.update({
            'action': 'update',
            'operacion_id': operacion.id,
            'tipo_servicio': 'Riego y drenaje',
            'prioridad': 'Alta',
            'estado': 'En Proceso',
        })
        update_response = self.client.post(reverse('operacion'), datos)

        self.assertRedirects(update_response, '/operacion/?ver=logistica')
        operacion.refresh_from_db()
        self.assertEqual(operacion.tipo_servicio, 'Riego Y Drenaje')
        self.assertEqual(operacion.prioridad, 'Alta')
        self.assertEqual(operacion.estado, 'En Proceso')

        delete_response = self.client.post(
            reverse('eliminar_operacion_programada', args=[operacion.id]),
        )
        self.assertRedirects(delete_response, '/operacion/?ver=logistica')
        self.assertFalse(ProgramacionOperacion.objects.filter(pk=operacion.pk).exists())


class CombustiblesInventoryTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin-combustibles-tests',
            email='admin-combustibles-tests@example.com',
            password='TestPassword@123',
        )
        self.client.force_login(self.admin)
        self.client.cookies['jwt_token'] = generate_jwt_token(self.admin)
        self.proveedor = Proveedor.objects.create(
            codigo='PROV-FUEL-01',
            nit='1234567-8',
            razon_social='Proveedor Combustible',
            nombre_propietario='Contacto Prueba',
            regimen_tributario='General',
            tipo_factura='Factura',
        )
        self.labor = Labor.objects.create(
            codigo='LAB-FUEL-01',
            descripcion='Aplicación de fertilizante',
            proceso='fertilizacion',
        )
        self.firma = FirmaAutorizada.objects.create(
            codigo='FIR-FUEL-01',
            nombre='Firma Autorizada Prueba',
            puesto='Encargado',
            area='Combustibles',
        )
        self.articulo = Articulo.objects.create(
            codigo_articulo='ART-DIESEL-01',
            descripcion='Diesel',
            unidad_medida='Galon',
            categoria='Combustible',
            stock=Decimal('20.00'),
        )
        self.tanque = TanqueCombustible.objects.create(
            codigo='TQ-TEST-01',
            nombre='Tanque de Prueba',
            tipo_combustible='Diésel',
            capacidad_galones=Decimal('100.00'),
            nivel_actual_galones=Decimal('20.00'),
            ubicacion='Patio de pruebas',
            estado='Operativo',
        )

    def datos_despacho(self, galones='8.25'):
        return {
            'no_vale': 'VAL-TEST-01',
            'fecha': '2026-10-02',
            'codigo_maquina': 'MAQ-TEST-01',
            'tipo_combustible': 'Diésel',
            'labor': self.labor.codigo,
            'galones': galones,
            'horometro_actual': '125.50',
            'operador': 'Operador Prueba',
            'estacion_tanque': self.tanque.codigo,
            'proveedor': self.proveedor.codigo,
            'despachado_por': self.firma.codigo,
            'finca': '',
        }

    def test_dispatch_reduces_selected_tank_and_creates_record_atomically(self):
        response = self.client.post(
            reverse('despacho_combustible'),
            self.datos_despacho(),
        )

        self.assertRedirects(response, reverse('despacho_combustible'))
        self.tanque.refresh_from_db()
        self.articulo.refresh_from_db()
        self.assertEqual(self.tanque.nivel_actual_galones, Decimal('11.75'))
        self.assertEqual(self.articulo.stock, Decimal('20.00'))
        despacho = DespachoCombustible.objects.get()
        self.assertEqual(despacho.no_vale, 'VAL-2026-0001')
        self.assertEqual(despacho.estacion_tanque.casefold(), self.tanque.codigo.casefold())
        self.assertEqual(despacho.labor, self.labor.descripcion)
        self.assertEqual(despacho.proveedor, self.proveedor.razon_social)
        self.assertEqual(despacho.despachado_por, self.firma.nombre)

    def test_dispatch_numbers_are_server_generated_and_autoincrement(self):
        first_response = self.client.post(reverse('despacho_combustible'), self.datos_despacho())
        second_response = self.client.post(
            reverse('despacho_combustible'),
            {**self.datos_despacho(galones='1.00'), 'no_vale': 'VAL-MODIFICADO'},
        )

        self.assertRedirects(first_response, reverse('despacho_combustible'))
        self.assertRedirects(second_response, reverse('despacho_combustible'))
        self.assertEqual(
            list(DespachoCombustible.objects.order_by('created_at').values_list('no_vale', flat=True)),
            ['VAL-2026-0001', 'VAL-2026-0002'],
        )

    def test_dispatch_number_does_not_reuse_a_deleted_vale(self):
        self.client.post(reverse('despacho_combustible'), self.datos_despacho())
        despacho = DespachoCombustible.objects.get()
        self.client.post(reverse('gestionar_despacho_combustible', args=[despacho.id]), {
            'action': 'delete',
        })
        self.client.post(reverse('despacho_combustible'), self.datos_despacho())

        despacho_nuevo = DespachoCombustible.objects.get()
        self.assertEqual(despacho_nuevo.no_vale, 'VAL-2026-0002')

    def test_dispatch_rejects_values_outside_the_catalogs(self):
        response = self.client.post(reverse('despacho_combustible'), {
            **self.datos_despacho(),
            'despachado_por': 'Persona No Autorizada',
        })

        self.assertRedirects(response, reverse('despacho_combustible'))
        self.assertFalse(DespachoCombustible.objects.exists())
        self.articulo.refresh_from_db()
        self.tanque.refresh_from_db()
        self.assertEqual(self.articulo.stock, Decimal('20.00'))
        self.assertEqual(self.tanque.nivel_actual_galones, Decimal('20.00'))

    def test_dispatch_above_stock_is_rejected_without_creating_record(self):
        response = self.client.post(
            reverse('despacho_combustible'),
            self.datos_despacho(galones='20.01'),
        )

        self.assertRedirects(response, reverse('despacho_combustible'))
        self.articulo.refresh_from_db()
        self.tanque.refresh_from_db()
        self.assertEqual(self.articulo.stock, Decimal('20.00'))
        self.assertEqual(self.tanque.nivel_actual_galones, Decimal('20.00'))
        self.assertFalse(DespachoCombustible.objects.exists())

    def test_dispatch_rejects_tank_with_a_different_fuel_type(self):
        tanque_regular = TanqueCombustible.objects.create(
            codigo='TQ-GAS-01',
            nombre='Tanque Gasolina',
            tipo_combustible='Gasolina Regular',
            capacidad_galones=Decimal('50.00'),
            nivel_actual_galones=Decimal('30.00'),
            ubicacion='Patio de pruebas',
            estado='Operativo',
        )

        response = self.client.post(reverse('despacho_combustible'), {
            **self.datos_despacho(),
            'estacion_tanque': tanque_regular.codigo,
        })

        self.assertRedirects(response, reverse('despacho_combustible'))
        self.assertFalse(DespachoCombustible.objects.exists())
        tanque_regular.refresh_from_db()
        self.assertEqual(tanque_regular.nivel_actual_galones, Decimal('30.00'))


    def test_recharge_above_capacity_is_rejected(self):
        response = self.client.post(reverse('tanques_combustible'), {
            'action': 'recarga',
            'codigo_tanque': self.tanque.codigo,
            'galones_recarga': '80.01',
        })

        self.assertRedirects(response, reverse('tanques_combustible'))
        self.tanque.refresh_from_db()
        self.assertEqual(self.tanque.nivel_actual_galones, Decimal('20.00'))

    def test_negative_tank_adjustment_is_rejected(self):
        response = self.client.post(reverse('tanques_combustible'), {
            'action': 'ajuste',
            'codigo_tanque': self.tanque.codigo,
            'nuevo_nivel': '-0.01',
            'estado': 'Operativo',
        })

        self.assertRedirects(response, reverse('tanques_combustible'))
        self.tanque.refresh_from_db()
        self.assertEqual(self.tanque.nivel_actual_galones, Decimal('20.00'))

    def test_tank_can_be_created_updated_and_deleted_without_history(self):
        datos = {
            'codigo': 'TQ-TEST-02',
            'nombre': 'Tanque Secundario',
            'tipo_combustible': 'Gasolina Regular',
            'capacidad_galones': '50.00',
            'nivel_actual_galones': '10.00',
            'ubicacion': 'Bodega Norte',
            'estado': 'Operativo',
        }
        create_response = self.client.post(reverse('tanques_combustible'), {
            **datos,
            'action': 'crear_tanque',
        })

        self.assertRedirects(create_response, reverse('tanques_combustible'))
        tanque = TanqueCombustible.objects.get(codigo='TQ-TEST-02')

        datos.update({
            'codigo': 'TQ-TEST-03',
            'codigo_original': tanque.codigo,
            'nombre': 'Tanque Patio',
            'capacidad_galones': '60.00',
            'nivel_actual_galones': '12.00',
        })
        edit_response = self.client.post(reverse('tanques_combustible'), {
            **datos,
            'action': 'editar_tanque',
        })

        self.assertRedirects(edit_response, reverse('tanques_combustible'))
        tanque.refresh_from_db()
        self.assertEqual(tanque.codigo, 'TQ-TEST-03')
        self.assertEqual(tanque.nivel_actual_galones, Decimal('12.00'))

        delete_response = self.client.post(reverse('tanques_combustible'), {
            'action': 'eliminar_tanque',
            'codigo_tanque': tanque.codigo,
        })
        self.assertRedirects(delete_response, reverse('tanques_combustible'))
        self.assertFalse(TanqueCombustible.objects.filter(pk=tanque.pk).exists())

    def test_tank_with_dispatch_history_cannot_be_deleted(self):
        self.client.post(reverse('despacho_combustible'), self.datos_despacho())

        response = self.client.post(reverse('tanques_combustible'), {
            'action': 'eliminar_tanque',
            'codigo_tanque': self.tanque.codigo,
        })

        self.assertRedirects(response, reverse('tanques_combustible'))
        self.assertTrue(TanqueCombustible.objects.filter(pk=self.tanque.pk).exists())
        self.tanque.refresh_from_db()
        self.assertEqual(self.tanque.nivel_actual_galones, Decimal('11.75'))

    def test_three_fuel_pages_render_crud_controls(self):
        self.client.post(reverse('despacho_combustible'), self.datos_despacho())

        dispatch_response = self.client.get(reverse('despacho_combustible'), {'ver': 'historial'})
        consumption_response = self.client.get(reverse('consumo_combustible'))
        tanks_response = self.client.get(reverse('tanques_combustible'))

        self.assertEqual(dispatch_response.status_code, 200)
        self.assertContains(dispatch_response, 'Editar')
        self.assertContains(dispatch_response, 'Eliminar')
        self.assertContains(dispatch_response, 'No. de Vale')
        self.assertContains(dispatch_response, 'Maquinaria *')
        self.assertContains(dispatch_response, 'Tanque *')
        self.assertContains(dispatch_response, 'TQ-TEST-01 - Tanque De Prueba')
        self.assertNotContains(dispatch_response, 'Maquinaria a Suministrar')
        self.assertContains(dispatch_response, 'Labor')
        self.assertContains(dispatch_response, 'Proveedor Combustible')
        self.assertContains(dispatch_response, 'Firma Autorizada Prueba')
        self.assertContains(dispatch_response, 'Historial de Vales')
        self.assertNotContains(dispatch_response, 'Historial de Vales y Cargas')
        self.assertNotContains(dispatch_response, 'Tanque Suministrador')
        self.assertContains(dispatch_response, 'Tipo de Combustible')
        self.assertContains(dispatch_response, 'Cantidad despachada')
        self.assertContains(dispatch_response, 'Horómetro de Despacho')
        self.assertContains(dispatch_response, '<th>Tanque</th>', html=True)
        self.assertEqual(consumption_response.status_code, 200)
        self.assertContains(consumption_response, 'Editar')
        self.assertContains(consumption_response, 'Eliminar')
        self.assertEqual(tanks_response.status_code, 200)
        self.assertContains(tanks_response, 'Nuevo Tanque')
        self.assertContains(tanks_response, 'Editar')
        self.assertContains(tanks_response, 'Eliminar')

    def test_edit_and_delete_dispatch_rebalance_selected_tank_stock(self):
        self.client.post(reverse('despacho_combustible'), self.datos_despacho())
        despacho = DespachoCombustible.objects.get()

        datos = self.datos_despacho(galones='5.00')
        datos.update({
            'action': 'update',
            'no_vale': 'VAL-TEST-02',
        })
        edit_response = self.client.post(
            reverse('gestionar_despacho_combustible', args=[despacho.id]),
            datos,
        )

        self.assertRedirects(edit_response, reverse('despacho_combustible') + '?ver=historial')
        self.tanque.refresh_from_db()
        despacho.refresh_from_db()
        self.assertEqual(self.tanque.nivel_actual_galones, Decimal('15.00'))
        self.assertEqual(despacho.no_vale, 'VAL-2026-0001')
        self.assertEqual(despacho.galones, Decimal('5.00'))
        self.assertEqual(despacho.proveedor, self.proveedor.razon_social)
        self.assertEqual(despacho.labor, self.labor.descripcion)

        delete_response = self.client.post(
            reverse('gestionar_despacho_combustible', args=[despacho.id]),
            {'action': 'delete', 'return_to': 'consumo'},
        )
        self.assertRedirects(delete_response, reverse('consumo_combustible'))
        self.tanque.refresh_from_db()
        self.assertEqual(self.tanque.nivel_actual_galones, Decimal('20.00'))
        self.assertFalse(DespachoCombustible.objects.exists())


class FiltroTipoMaquinariaTests(TestCase):
    def setUp(self):
        user = User.objects.create_superuser(
            username='fleet-filter-user',
            email='fleet-filter-user@example.com',
            password='Valid-User4!Pass',
        )
        self.client.force_login(user)
        self.client.cookies['jwt_token'] = generate_jwt_token(user)

        self.tractor = Maquinaria.objects.create(
            codigo_maquina='M-FILTRO-01',
            combustible='Diésel',
            tipo_maquina='Tractor',
            marca_maquina='Marca A',
            serie_maquina='SERIE-01',
            placa_matricula='P-001',
        )
        Maquinaria.objects.create(
            codigo_maquina='M-FILTRO-02',
            combustible='Diésel',
            tipo_maquina='Camión',
            marca_maquina='Marca B',
            serie_maquina='SERIE-02',
            placa_matricula='P-002',
        )

    def test_type_filter_limits_fleet_and_remains_selected(self):
        response = self.client.get(reverse('estado_maquinaria'), {
            'tipo_maquina': 'Tractor',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item['maquina'] for item in response.context['flota']],
            [self.tractor],
        )
        self.assertEqual(response.context['filtro_tipo_maquina'], 'Tractor')
        self.assertContains(response, 'value="Tractor" selected')


class AreaLoteLimitTests(TestCase):
    def setUp(self):
        admin = User.objects.create_superuser(
            username='admin-area-lote-limit',
            email='admin-area-lote-limit@example.com',
            password='TestPassword@123',
        )
        self.client.force_login(admin)
        self.client.cookies['jwt_token'] = generate_jwt_token(admin)
        Cuenta.objects.all().delete()
        Labor.objects.create(codigo='LAB-RIEGO-SIN-CUENTA', descripcion='Riego sin cuenta', proceso='riego')
        Labor.objects.create(codigo='LAB-AREA', descripcion='Siembra de prueba', proceso='siembras')
        Cuenta.objects.create(codigo='CTA-SIEMBRA', descripcion='Cuenta de siembras', proceso='siembras')

    def datos_registro(self, area):
        return {
            'no_boleta': f'AREA-{area}',
            'fecha_labor': '2026-10-02',
            'tipo_servicio': 'Preparación de suelo',
            'proveedor': 'Proveedor de Prueba',
            'finca': 'Finca Central',
            'lote': '0010',
            'area_lote': area,
            'codigo_labor': 'LAB-AREA',
        }

    def test_area_lote_accepts_150_hectares(self):
        response = self.client.post(reverse('registros'), self.datos_registro('150.00'))

        self.assertRedirects(response, reverse('registros'))
        registro = RegistroOperativo.objects.get(no_boleta='AREA-150.00')
        self.assertEqual(registro.area_lote, Decimal('150.00'))
        self.assertEqual(registro.cuenta_contable, 'CTA-SIEMBRA')

    def test_operational_record_uses_the_account_for_the_selected_labor_process(self):
        Labor.objects.create(codigo='LAB-RIEGO', descripcion='Riego por prueba', proceso='riego')
        Cuenta.objects.create(codigo='CTA-RIEGO', descripcion='Cuenta de riego', proceso='riego')

        self.client.post(reverse('registros'), {
            **self.datos_registro('10.00'),
            'no_boleta': 'AREA-RIEGO',
            'codigo_labor': 'LAB-RIEGO',
        })

        registro = RegistroOperativo.objects.get(no_boleta='AREA-RIEGO')
        self.assertEqual(registro.labor, 'Riego Por Prueba')
        self.assertEqual(registro.cuenta_contable, 'CTA-RIEGO')

    def test_operational_record_is_rejected_when_process_has_no_account(self):
        response = self.client.post(reverse('registros'), {
            **self.datos_registro('10.00'),
            'no_boleta': 'AREA-SIN-CUENTA',
            'codigo_labor': 'LAB-RIEGO-SIN-CUENTA',
        })

        self.assertRedirects(response, reverse('registros'))
        self.assertFalse(RegistroOperativo.objects.filter(no_boleta='AREA-SIN-CUENTA').exists())

    def test_transport_locations_are_saved_only_for_allowed_services(self):
        for index, service in enumerate((
            'Envio de semilla de caña',
            'Transporte de personal',
            'Viajes de material o maquinaria',
        ), start=1):
            with self.subTest(service=service):
                response = self.client.post(reverse('registros'), {
                    **self.datos_registro(f'20.{index:02d}'),
                    'no_boleta': f'TRANSPORTE-{index}',
                    'tipo_servicio': service,
                    'lugar_origen': 'Guatemala',
                    'lugar_destino': 'Quetzaltenango',
                })
                self.assertRedirects(response, reverse('registros'))
                registro = RegistroOperativo.objects.get(no_boleta=f'TRANSPORTE-{index}')
                self.assertEqual(registro.lugar_origen, 'Guatemala')
                self.assertEqual(registro.lugar_destino, 'Quetzaltenango')

    def test_transport_locations_are_not_saved_for_other_services(self):
        self.client.post(reverse('registros'), {
            **self.datos_registro('20.00'),
            'no_boleta': 'SIN-TRANSPORTE',
            'tipo_servicio': 'Preparación de suelo',
            'lugar_origen': 'Guatemala',
            'lugar_destino': 'Quetzaltenango',
        })

        registro = RegistroOperativo.objects.get(no_boleta='SIN-TRANSPORTE')
        self.assertIsNone(registro.lugar_origen)
        self.assertIsNone(registro.lugar_destino)

    def test_area_lote_above_150_is_rejected(self):
        response = self.client.post(reverse('registros'), self.datos_registro('150.01'))

        self.assertRedirects(response, reverse('registros'))
        self.assertFalse(RegistroOperativo.objects.filter(no_boleta='AREA-150.01').exists())


class SemillaCanaSourceTests(TestCase):
    def setUp(self):
        admin = User.objects.create_superuser(
            username='admin-semilla-source',
            email='admin-semilla-source@example.com',
            password='TestPassword@123',
        )
        self.client.force_login(admin)
        self.client.cookies['jwt_token'] = generate_jwt_token(admin)
        Cuenta.objects.all().delete()
        Labor.objects.create(codigo='LAB-SEMILLA', descripcion='Siembra de semilla', proceso='siembras')
        Cuenta.objects.create(codigo='CTA-SEMILLA', descripcion='Cuenta de siembras', proceso='siembras')

    def datos_envio_semilla(self, **overrides):
        datos = {
            'no_boleta': 'SEMILLA-ORIGEN-01',
            'fecha_labor': '2026-10-02',
            'tipo_servicio': 'Envio de semilla de caña',
            'proveedor': 'Proveedor de Prueba',
            'finca': 'Finca Destino',
            'lote': 'Lote Destino',
            'area_lote': '12.00',
            'codigo_labor': 'LAB-SEMILLA',
            'corte_semilla': '1',
            'finca_corte_semilla': 'Finca Origen',
            'lote_corte_semilla': 'Lote 8',
            'variedad': 'Variedad de Prueba',
            'total_paquetes': '15',
            'peso_kg': '225.00',
        }
        datos.update(overrides)
        return datos

    def test_seed_cut_saves_origin_farm_and_lot(self):
        response = self.client.post(reverse('registros'), self.datos_envio_semilla())

        self.assertRedirects(response, reverse('registros'))
        registro = RegistroOperativo.objects.get(no_boleta='SEMILLA-ORIGEN-01')
        self.assertEqual(registro.finca_corte_semilla, 'Finca Origen')
        self.assertEqual(registro.lote_corte_semilla, 'Lote 8')

    def test_seed_cut_requires_origin_farm_and_lot(self):
        response = self.client.post(reverse('registros'), self.datos_envio_semilla(lote_corte_semilla=''))

        self.assertRedirects(response, reverse('registros'))
        self.assertFalse(RegistroOperativo.objects.filter(no_boleta='SEMILLA-ORIGEN-01').exists())

    def test_other_services_do_not_save_cane_details(self):
        response = self.client.post(reverse('registros'), self.datos_envio_semilla(
            no_boleta='SERVICIO-SIN-SEMILLA',
            tipo_servicio='Aplicaciones aereas',
        ))

        self.assertRedirects(response, reverse('registros'))
        registro = RegistroOperativo.objects.get(no_boleta='SERVICIO-SIN-SEMILLA')
        self.assertIsNone(registro.corte_semilla)
        self.assertIsNone(registro.finca_corte_semilla)
        self.assertIsNone(registro.lote_corte_semilla)
        self.assertIsNone(registro.variedad)
        self.assertIsNone(registro.total_paquetes)
        self.assertIsNone(registro.peso_kg)

    def test_edit_updates_seed_cut_origin(self):
        registro = RegistroOperativo.objects.create(
            no_boleta='SEMILLA-EDITAR-01',
            fecha_labor='2026-10-02',
            tipo_servicio='Envio de semilla de caña',
            proveedor='Proveedor de Prueba',
            finca='Finca Destino',
            lote='Lote Destino',
            corte_semilla='1',
            finca_corte_semilla='Finca Anterior',
            lote_corte_semilla='Lote Anterior',
        )

        response = self.client.post(reverse('editar_registro', args=[registro.id]), {
            'tipo_servicio': 'Envio de semilla de caña',
            'corte_semilla': '1',
            'finca_corte_semilla': 'Finca Nueva',
            'lote_corte_semilla': 'Lote 12',
        })

        self.assertRedirects(response, reverse('registros_data'))
        registro.refresh_from_db()
        self.assertEqual(registro.finca_corte_semilla, 'Finca Nueva')
        self.assertEqual(registro.lote_corte_semilla, 'Lote 12')


class ProcesosLaborTests(TestCase):
    def setUp(self):
        admin = User.objects.create_superuser(
            username='admin-procesos-labor',
            email='admin-procesos-labor@example.com',
            password='TestPassword@123',
        )
        self.client.force_login(admin)
        self.client.cookies['jwt_token'] = generate_jwt_token(admin)

    def test_catalog_has_five_labor_options_per_process(self):
        response = self.client.get(reverse('api_labores'))

        self.assertEqual(response.status_code, 200)
        labores = response.json()
        self.assertEqual(len(labores), 15)
        for proceso in ('siembras', 'fertilizacion', 'riego'):
            with self.subTest(proceso=proceso):
                self.assertEqual(sum(labor['proceso'] == proceso for labor in labores), 5)

    def test_creation_and_edit_forms_group_labor_options(self):
        create_response = self.client.get(reverse('registros'))
        registro = RegistroOperativo.objects.create(
            no_boleta='PROCESOS-LABOR-EDITAR',
            fecha_labor='2026-10-02',
            tipo_servicio='Envio de semilla de caña',
            proveedor='Proveedor de Prueba',
            finca='Finca Central',
            lote='Lote 1',
            labor='Siembra de maíz en surcos',
            corte_semilla='2',
        )
        edit_response = self.client.get(reverse('editar_registro', args=[registro.id]))

        for response in (create_response, edit_response):
            with self.subTest(status=response.status_code):
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, '<optgroup label="Siembras">')
                self.assertContains(response, '<optgroup label="Fertilización">')
                self.assertContains(response, '<optgroup label="Riego">')
