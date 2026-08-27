from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver


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
