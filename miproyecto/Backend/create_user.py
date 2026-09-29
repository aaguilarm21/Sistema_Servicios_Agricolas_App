import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuraciones.miproyecto.settings')

import django
django.setup()

from django.core.management import call_command

call_command('ensureadmin')
