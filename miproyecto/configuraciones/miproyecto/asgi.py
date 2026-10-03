"""
Configuración ASGI para el proyecto miproyecto.

Expone la aplicación ASGI mediante la variable de módulo ``application``.

Más información:
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miproyecto.settings')

application = get_asgi_application()
