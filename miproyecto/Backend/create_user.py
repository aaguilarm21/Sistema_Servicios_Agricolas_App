import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miproyecto.settings')

import django
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    print('Usuario admin creado exitosamente')
else:
    print('El usuario admin ya existe')
