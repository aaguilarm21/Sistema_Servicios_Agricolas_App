from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
import re
import unicodedata


class CustomAuthenticationForm(auth_forms.AuthenticationForm):
    error_messages = {
        'invalid_login': _(
            'Por favor ingresa un usuario y contraseña correctos.'
        ),
        'inactive': _(
            'USUARIO INACTIVO, COMUNIQUESE CON EL ADMIN, PARA ACTIVARLO'
        ),
    }


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

