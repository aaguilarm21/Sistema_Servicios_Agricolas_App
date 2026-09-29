import jwt
from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.cache import patch_vary_headers
from .device_detection import detect_device_type
from .jwt_utils import decode_jwt_token


class DeviceDetectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.device_type = detect_device_type(request.META.get('HTTP_USER_AGENT', ''))
        request.is_mobile_device = request.device_type in {'mobile', 'tablet'}
        response = self.get_response(request)
        patch_vary_headers(response, ('User-Agent',))
        return response


class JWTMiddleware:
    """
    Middleware de seguridad que valida tokens JWT para proteger las rutas de la aplicación.
    Soporta extracción de token desde la cookie HTTP-Only 'jwt_token' o del encabezado 'Authorization: Bearer <token>'.
    """

    EXEMPT_URLS = [
        '/accounts/login/',
        '/accounts/ajax-login/',
        '/accounts/signup/',
        '/accounts/logout/',
        '/admin/login/',
    ]

    EXEMPT_PREFIXES = [
        '/static/',
        '/media/',
        '/admin/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Verificar si la ruta es exenta de validación JWT
        if self._is_exempt(path):
            return self.get_response(request)

        # Intentar extraer el token JWT
        token = self._extract_token(request)

        if not token:
            return self._handle_unauthorized(request, 'Token de autenticación JWT no proporcionado.')

        try:
            payload = decode_jwt_token(token)
            user_id = payload.get('user_id')
            user = User.objects.filter(pk=user_id).first()

            if not user or not user.is_active:
                return self._handle_unauthorized(request, 'El usuario asociado al token no existe o está bloqueado/inactivo.')

            # Autenticar explícitamente el objeto request
            request.user = user
            request.jwt_payload = payload

        except jwt.ExpiredSignatureError:
            return self._handle_unauthorized(request, 'La sesión JWT ha expirado. Por favor inicie sesión de nuevo.')
        except jwt.PyJWTError:
            return self._handle_unauthorized(request, 'Token JWT inválido o corrupto.')
        except Exception:
            return self._handle_unauthorized(request, 'Error al validar la seguridad JWT.')

        return self.get_response(request)

    def _is_exempt(self, path):
        if path in self.EXEMPT_URLS:
            return True
        for prefix in self.EXEMPT_PREFIXES:
            if path.startswith(prefix):
                return True
        return False

    def _extract_token(self, request):
        # 1. Buscar en la cookie HTTP-Only 'jwt_token'
        token = request.COOKIES.get('jwt_token')
        if token:
            return token

        # 2. Buscar en el encabezado Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            return auth_header.split(' ', 1)[1].strip()

        return None

    def _handle_unauthorized(self, request, error_message):
        # Si la petición es AJAX o espera JSON
        is_ajax = (
            request.headers.get('x-requested-with') == 'XMLHttpRequest' or
            'application/json' in request.headers.get('accept', '').lower() or
            request.content_type == 'application/json' or
            '/api/' in request.path or
            request.path == '/registros-data/'
        )

        if is_ajax:
            return JsonResponse({
                'success': False,
                'error': error_message,
                'code': 'jwt_unauthorized'
            }, status=401)

        # Redirigir a login para navegación web estándar
        login_url = reverse('login') if hasattr(reverse, '__call__') else '/accounts/login/'
        return redirect(f"{login_url}?next={request.path}")
