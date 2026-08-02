import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class PasswordStandardValidator:
    """
    Validador personalizado de contraseñas para verificar presencia de:
    - Longitud mínima de 8 caracteres.
    - Al menos una letra mayúscula.
    - Al menos una letra minúscula.
    - Al menos un número.
    - Al menos un carácter especial (!@#$%^&*()_+-=[]{}|;:,.<>?/).
    """

    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if not password:
            raise ValidationError(
                _('La contraseña no puede estar vacía.'),
                code='password_empty',
            )

        if len(password) < self.min_length:
            raise ValidationError(
                _(f'La contraseña debe tener al menos {self.min_length} caracteres.'),
                code='password_too_short',
            )

        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _('La contraseña debe incluir al menos una letra mayúscula (A-Z).'),
                code='password_no_upper',
            )

        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _('La contraseña debe incluir al menos una letra minúscula (a-z).'),
                code='password_no_lower',
            )

        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _('La contraseña debe incluir al menos un número (0-9).'),
                code='password_no_number',
            )

        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?/]', password):
            raise ValidationError(
                _('La contraseña debe incluir al menos un carácter especial (!@#$%^&*()_+-=[]{}|;:,.<>?/).'),
                code='password_no_symbol',
            )

    def get_help_text(self):
        return _(
            'Su contraseña debe contener al menos 8 caracteres, incluyendo al menos una mayúscula, '
            'una minúscula, un número y un carácter especial (!@#$%^&*()_+-=[]{}|;:,.<>?/).'
        )
