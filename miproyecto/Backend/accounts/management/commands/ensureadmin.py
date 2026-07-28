from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates or updates a default admin user for the project.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'admin'
        email = 'admin@sistema.local'
        password = 'Admin123!'

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            },
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Admin user created: {username}'))
        else:
            if not user.check_password(password):
                user.set_password(password)
                user.save()
            self.stdout.write(self.style.WARNING(f'Admin user already exists: {username}'))

        Group.objects.get_or_create(name='Admin')
        Group.objects.get_or_create(name='Usuario')
        user.groups.clear()
        user.groups.add(Group.objects.get(name='Admin'))
