from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
from decimal import Decimal

from .models import Empleado, FirmaAutorizada, RegistroOperativo
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
        self.assertEqual(self.registro.lote, 'Lote actualizado')
