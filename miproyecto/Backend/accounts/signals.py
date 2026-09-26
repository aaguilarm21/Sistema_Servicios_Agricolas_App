from decimal import Decimal, InvalidOperation
import ipaddress

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .device_detection import detect_device_type
from .models import LoginAttempt


def _location_data(request):
    if request is None or request.POST.get('share_location') != 'yes':
        return None, None, 'not_shared'

    try:
        latitude = Decimal(request.POST.get('latitude', ''))
        longitude = Decimal(request.POST.get('longitude', ''))
        if (
            latitude.is_finite()
            and longitude.is_finite()
            and -90 <= latitude <= 90
            and -180 <= longitude <= 180
        ):
            return latitude, longitude, 'captured'
    except (InvalidOperation, TypeError, ValueError):
        pass

    status = request.POST.get('location_status')
    if status in {'denied', 'unavailable'}:
        return None, None, status
    return None, None, 'unavailable'


def registrar_intento_acceso(request, username='', user=None, successful=False):
    if request is not None and getattr(request, '_login_attempt_logged', False):
        return

    user_agent = request.META.get('HTTP_USER_AGENT', '') if request is not None else ''
    ip_value = request.META.get('REMOTE_ADDR') if request is not None else None
    try:
        ip_address = str(ipaddress.ip_address(ip_value)) if ip_value else None
    except ValueError:
        ip_address = None

    latitude, longitude, location_status = _location_data(request)
    LoginAttempt.objects.create(
        user=user,
        username_attempt=(username or '')[:150],
        successful=successful,
        ip_address=ip_address,
        user_agent=user_agent[:1000],
        device_type=detect_device_type(user_agent),
        latitude=latitude,
        longitude=longitude,
        location_status=location_status,
    )
    if request is not None:
        request._login_attempt_logged = True


@receiver(user_logged_in)
def record_successful_login(sender, request, user, **kwargs):
    registrar_intento_acceso(request, username=user.get_username(), user=user, successful=True)


@receiver(user_login_failed)
def record_failed_login(sender, credentials, request, **kwargs):
    username = credentials.get(get_user_model().USERNAME_FIELD, '')
    registrar_intento_acceso(request, username=username, successful=False)


@receiver(post_migrate)
def ensure_default_groups(sender, **kwargs):
    """Crea los grupos por defecto y el usuario administrador por defecto tras ejecutar las migraciones."""
    if sender.name != apps.get_app_config('accounts').name:
        return

    Group.objects.get_or_create(name='Admin')
    Group.objects.get_or_create(name='Usuario')

    User = get_user_model()
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@sistema.local',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
        },
    )

    if created:
        user.set_password('Admin123!')
        user.save()
    elif not user.check_password('Admin123!'):
        user.set_password('Admin123!')
        user.save()

    user.groups.clear()
    user.groups.add(Group.objects.get(name='Admin'))
