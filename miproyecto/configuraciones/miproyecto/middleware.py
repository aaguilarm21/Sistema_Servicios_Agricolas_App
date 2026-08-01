from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render


class SafeExceptionMiddleware:
    """Captura excepciones inesperadas y devuelve una respuesta segura."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception:
            if getattr(settings, 'DEBUG', False):
                raise

            if request.path.startswith('/static/') or request.path.startswith('/media/'):
                return HttpResponse('Error interno del servidor.', status=500)

            try:
                return render(
                    request,
                    'home.html',
                    {
                        'request': request,
                        'error': 'Ha ocurrido un error inesperado. Intente nuevamente.',
                    },
                    status=500,
                )
            except Exception:
                return HttpResponse('Ha ocurrido un error inesperado. Intente nuevamente.', status=500)
