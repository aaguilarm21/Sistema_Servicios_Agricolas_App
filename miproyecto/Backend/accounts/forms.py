from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, User
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
import re
import unicodedata

from .validators import PasswordStandardValidator


class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': _(
            'Por favor ingresa un usuario y contraseña correctos.'
        ),
        'inactive': _(
            'USUARIO INACTIVO/BLOQUEADO, COMUNÍQUESE CON EL ADMINISTRADOR PARA ACTIVARLO'
        ),
        'rate_limited': _(
            'El usuario ha sido bloqueado por haber superado los 3 intentos fallidos de inicio de sesión. Por favor comuníquese con el administrador.'
        ),
    }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if request is None and args:
            request = args[0]
            args = args[1:]
        self.request = request
        super().__init__(request=request, *args, **kwargs)

    def _rate_limit_key(self, username):
        if not self.request:
            return None
        ip_address = self.request.META.get('REMOTE_ADDR', 'unknown')
        normalized_username = (username or '').strip().lower()
        if normalized_username:
            return f'login_attempts:{ip_address}:{normalized_username}'
        return f'login_attempts:{ip_address}'

    def _get_rate_limit_settings(self):
        attempts = getattr(settings, 'LOGIN_RATE_LIMIT_ATTEMPTS', 3)
        timeout = getattr(settings, 'LOGIN_RATE_LIMIT_LOCKOUT_SECONDS', 300)
        return attempts, timeout

    def _is_locked(self, username):
        key = self._rate_limit_key(username)
        if not key:
            return False
        attempts, _ = self._get_rate_limit_settings()
        current_attempts = cache.get(key, 0)
        return current_attempts >= attempts

    def _record_failure(self, username):
        key = self._rate_limit_key(username)
        if not key:
            return 1
        _, timeout = self._get_rate_limit_settings()
        current_attempts = cache.get(key, 0) + 1
        cache.set(key, current_attempts, timeout=timeout)
        return current_attempts

    def _clear_attempts(self, username):
        key = self._rate_limit_key(username)
        if key:
            cache.delete(key)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username:
            username = username.strip()
            self.cleaned_data['username'] = username

        if not username or not password:
            return self.cleaned_data

        user_obj = User.objects.filter(username__iexact=username).first()

        # Si el usuario ya está inactivo/bloqueado
        if user_obj and not user_obj.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

        # Si ya superó los 3 intentos previamente
        if self._is_locked(username):
            if user_obj and user_obj.is_active:
                user_obj.is_active = False
                user_obj.save(update_fields=['is_active'])
            raise forms.ValidationError(
                self.error_messages['rate_limited'],
                code='rate_limited',
            )

        user = authenticate(self.request, username=username, password=password)
        if user is None:
            failed_count = self._record_failure(username)
            max_attempts, _ = self._get_rate_limit_settings()

            if failed_count >= max_attempts:
                if user_obj and user_obj.is_active:
                    user_obj.is_active = False
                    user_obj.save(update_fields=['is_active'])
                raise forms.ValidationError(
                    self.error_messages['rate_limited'],
                    code='rate_limited',
                )

            remaining = max_attempts - failed_count
            raise forms.ValidationError(
                f"Por favor ingresa un usuario y contraseña correctos. (Intento fallido {failed_count} de {max_attempts}. Le quedan {remaining} intento(s)).",
                code='invalid_login',
            )

        self.user_cache = user
        self._clear_attempts(username)
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

        self.confirm_login_allowed(user)
        return self.cleaned_data


class AdminUserCreationForm(forms.Form):
    full_name = forms.CharField(
        label='Nombre completo',
        max_length=150,
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )
    username = forms.CharField(
        label='Usuario',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'readonly': 'readonly',
            'autocomplete': 'off'
        })
    )
    puesto = forms.CharField(
        label='Puesto',
        max_length=150,
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )
    rol = forms.ModelChoiceField(
        label='Rol',
        queryset=Group.objects.all(),
        empty_label=None,
        widget=forms.Select(attrs={'autocomplete': 'off'})
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'autocomplete': 'off'})
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'autocomplete': 'off'})
    )

    def clean(self):
        cleaned_data = super().clean()
        full_name = cleaned_data.get('full_name', '').strip()
        if not full_name:
            raise forms.ValidationError('Debes ingresar el nombre completo.')

        cleaned_data['username'] = self.generate_username(full_name)

        pwd1 = cleaned_data.get('password1')
        pwd2 = cleaned_data.get('password2')
        if pwd1 and pwd2 and pwd1 != pwd2:
            raise forms.ValidationError('Las contraseñas no coinciden.')

        if pwd1:
            validator = PasswordStandardValidator()
            validator.validate(pwd1)

        return cleaned_data

    def generate_username(self, full_name):
        name = unicodedata.normalize('NFKD', full_name).encode('ascii', 'ignore').decode('ascii')
        parts = [part for part in name.lower().split() if part]
        if not parts:
            return ''
        first_initial = parts[0][0]
        first_surname = parts[1] if len(parts) > 1 else parts[0]
        username = f'{first_initial}{first_surname}'
        username = re.sub(r'[^a-z0-9]', '', username)
        return username
