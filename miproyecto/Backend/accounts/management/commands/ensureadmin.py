import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Aprovisiona el administrador indicado mediante variables de entorno.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.getenv('DJANGO_ADMIN_USERNAME', '').strip()
        email = os.getenv('DJANGO_ADMIN_EMAIL', '').strip()
        password = os.getenv('DJANGO_ADMIN_PASSWORD', '')

        existing_admins = User.objects.filter(is_superuser=True)
        if not username or not password:
            existing_admin = existing_admins.first()
            if existing_admin:
                self.stdout.write(self.style.WARNING(
                    f'El administrador {existing_admin.username} ya existe; no se modificó.'
                ))
                return
            raise CommandError(
                'Define DJANGO_ADMIN_USERNAME y DJANGO_ADMIN_PASSWORD para aprovisionar el administrador.'
            )

        user = User.objects.filter(username=username).first()
        if user and not user.is_superuser:
            raise CommandError(f'El usuario {username} ya existe y no es administrador.')
        if existing_admins.exists() and not user:
            raise CommandError(
                'Ya existe otro administrador; DJANGO_ADMIN_USERNAME debe coincidir con uno existente.'
            )

        try:
            validate_password(password, user=user)
        except ValidationError as error:
            raise CommandError('; '.join(error.messages)) from error

        Group.objects.get_or_create(name='Admin')
        Group.objects.get_or_create(name='Usuario')

        if user:
            if not user.check_password(password):
                user.set_password(password)
                user.save(update_fields=['password'])
            self.stdout.write(self.style.SUCCESS(f'Administrador {username} verificado.'))
        else:
            user = User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Administrador {username} creado.'))

        user.groups.add(Group.objects.get(name='Admin'))
