import jwt
from datetime import datetime, timedelta, timezone as dt_timezone
from django.conf import settings
from django.contrib.auth.models import User

JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 8  # Duración del token


def generate_jwt_token(user: User) -> str:
    """
    Genera un token JWT para el usuario autenticado conteniendo sus claims principales.
    """
    now = datetime.now(dt_timezone.utc)
    payload = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email or '',
        'is_superuser': user.is_superuser,
        'is_staff': user.is_staff,
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(hours=JWT_EXPIRATION_HOURS)).timestamp()),
    }
    secret_key = getattr(settings, 'SECRET_KEY', 'dev-only-insecure-secret-key')
    token = jwt.encode(payload, secret_key, algorithm=JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token


def decode_jwt_token(token: str) -> dict:
    """
    Decodifica y valida la firma y expiración de un token JWT.
    Retorna el payload si es válido, o lanza jwt.PyJWTError si no lo es.
    """
    secret_key = getattr(settings, 'SECRET_KEY', 'dev-only-insecure-secret-key')
    payload = jwt.decode(token, secret_key, algorithms=[JWT_ALGORITHM])
    return payload
