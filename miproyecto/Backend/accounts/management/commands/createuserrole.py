import secrets
import string

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Crear Usuario con un Rol (admin o usuario)."

    def add_arguments(self, parser):
        parser.add_argument('--name', help='Nombre completo del usuario (se utiliza para generar el nombre de usuario si no se proporciona)')
        parser.add_argument('--username', help='Nombre de usuario para el nuevo usuario (generado a partir del nombre si no se proporciona)')
        parser.add_argument('--password', help='Contraseña para el nuevo usuario (se generará aleatoriamente si no se proporciona)')
        parser.add_argument(
            '--email',
            default='',
            help='Dirección de correo electrónico del nuevo usuario (opcional)',
        )
        parser.add_argument(
            '--role',
            choices=['admin', 'usuario'],
            default='usuario',
            help='Rol a asignar: admin o usuario (por defecto, usuario)',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        name = (options.get('name') or '').strip()
        username = (options.get('username') or '').strip()
        password = (options.get('password') or '').strip()
        email = options['email']
        role = options['role']

        # Generar nombre de usuario si no se proporciona
        if not username:
            if not name:
                raise CommandError("Debe proporcionar --name o --username.")
            username = name.lower().replace(' ', '_').replace('-', '_')

        # Generar contraseña si no se proporciona
        if not password:
            if role == 'admin':
                password = 'Admin2026'
            else:
                password = 'User2026'

        if User.objects.filter(username=username).exists():
            raise CommandError(f"El usuario '{username}' ya existe.")

        is_staff = False
        is_superuser = False
        group_name = 'Usuario'

        if role == 'admin':
            is_staff = True
            is_superuser = True
            group_name = 'Admin'

        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.save()

        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)

        self.stdout.write(self.style.SUCCESS(f"Usuario '{username}' creado con rol '{role}'."))
        self.stdout.write(f"Usuario: {username}")
        self.stdout.write(f"Contraseña temporal: {password}")
        self.stdout.write("Recuerda cambiar la contraseña después del primer inicio de sesión.")

    def generate_temporary_password(self):
        """Genera una contraseña temporal segura."""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for _ in range(12))
        return password
