from decimal import Decimal, InvalidOperation
import ipaddress

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db.models.signals import post_delete, post_migrate, post_save
from django.dispatch import receiver

from .catalog_cache import invalidar_cache_catalogo_modulo
from .device_detection import detectar_tipo_dispositivo
from .models import (
    Auxiliar, Cuenta, Empleado, FirmaAutorizada, Labor, LoginAttempt, Maquinaria,
    Municipio, Proveedor, TanqueCombustible, Variedad,
)

# Señales y funciones auxiliares para registrar intentos de acceso al sistema.
# También se crean automáticamente los grupos de roles al ejecutar migraciones.


def _datos_ubicacion(peticion):
    if peticion is None or peticion.POST.get('share_location') != 'yes':
        return None, None, 'not_shared'

    try:
        latitud = Decimal(peticion.POST.get('latitude', ''))
        longitud = Decimal(peticion.POST.get('longitude', ''))
        if (
            latitud.is_finite()
            and longitud.is_finite()
            and -90 <= latitud <= 90
            and -180 <= longitud <= 180
        ):
            return latitud, longitud, 'captured'
    except (InvalidOperation, TypeError, ValueError):
        pass

    estado = peticion.POST.get('location_status')
    if estado in {'denied', 'unavailable'}:
        return None, None, estado
    return None, None, 'unavailable'


def registrar_intento_acceso(peticion, nombre_usuario='', usuario=None, exitoso=False):
    if peticion is not None and getattr(peticion, '_login_attempt_logged', False):
        return

    agente_usuario = peticion.META.get('HTTP_USER_AGENT', '') if peticion is not None else ''
    valor_ip = peticion.META.get('REMOTE_ADDR') if peticion is not None else None
    try:
        direccion_ip = str(ipaddress.ip_address(valor_ip)) if valor_ip else None
    except ValueError:
        direccion_ip = None

    latitud, longitud, estado_ubicacion = _datos_ubicacion(peticion)
    LoginAttempt.objects.create(
        user=usuario,
        username_attempt=(nombre_usuario or '')[:150],
        successful=exitoso,
        ip_address=direccion_ip,
        user_agent=agente_usuario[:1000],
        device_type=detectar_tipo_dispositivo(agente_usuario),
        latitude=latitud,
        longitude=longitud,
        location_status=estado_ubicacion,
    )
    if peticion is not None:
        peticion._login_attempt_logged = True


@receiver(user_logged_in)
def registrar_login_exitoso(sender, request, user, **kwargs):
    """Registra en el log de intentos cuando un inicio de sesión es exitoso."""
    registrar_intento_acceso(
        request,
        nombre_usuario=user.get_username(),
        usuario=user,
        exitoso=True,
    )


@receiver(user_login_failed)
def registrar_login_fallido(sender, credentials, request, **kwargs):
    """Registra en el log de intentos cuando un inicio de sesión falla."""
    username = credentials.get(get_user_model().USERNAME_FIELD, '')
    registrar_intento_acceso(request, nombre_usuario=username, exitoso=False)


@receiver(post_migrate)
def asegurar_grupos_predeterminados(sender, **kwargs):
    """Crea los grupos de autorización requeridos por la aplicación."""
    if sender.name != apps.get_app_config('accounts').name:
        return

    Group.objects.get_or_create(name='Admin')
    Group.objects.get_or_create(name='Usuario')


_MODELOS_CATALOGO_MODULO = (
    Auxiliar, Cuenta, Empleado, FirmaAutorizada, Labor, Maquinaria, Municipio,
    Proveedor, TanqueCombustible, Variedad,
)

for modelo in _MODELOS_CATALOGO_MODULO:
    post_save.connect(
        invalidar_cache_catalogo_modulo,
        sender=modelo,
        dispatch_uid=f'accounts.invalidar_cache_catalogo_modulo.save.{modelo._meta.label_lower}',
    )
    post_delete.connect(
        invalidar_cache_catalogo_modulo,
        sender=modelo,
        dispatch_uid=f'accounts.invalidar_cache_catalogo_modulo.delete.{modelo._meta.label_lower}',
    )
