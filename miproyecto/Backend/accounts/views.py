from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
import logging
import re
from datetime import timedelta

from .jwt_utils import generate_jwt_token
from .forms import AdminUserCreationForm, CustomAuthenticationForm
from .signals import registrar_intento_acceso
from .models import (
    UserProfile, Proveedor, Empleado, Maquinaria, Bodega, Articulo,
    Labor, Cuenta, UnidadMedida, NombrePuesto, Variedad, TipoMaquina, Marca, Municipio, Auxiliar,
    LoginAttempt, CAMPOS_IDENTIFICACION, normalizar_texto,
)

logger = logging.getLogger(__name__)


# Vistas de autenticación, registro de usuarios y APIs internas.
# Aquí se centraliza el inicio de sesión, el cambio de usuario desde el panel,
# la creación de nuevos usuarios y la administración de estados y roles.


def normalizar_datos(data):
    """Normaliza el texto de los campos del formulario, exceptuando campos de identificación."""
    return {
        campo: valor if campo in CAMPOS_IDENTIFICACION or campo == 'puesto' else normalizar_texto(valor)
        for campo, valor in data.items()
    }


# Vista personalizada para el inicio de sesión del sistema.
class CustomLoginView(LoginView):
    """
    Vista personalizada de inicio de sesión.
    Genera y guarda el token JWT en cookie segura tras autenticación exitosa.
    """
    authentication_form = CustomAuthenticationForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = False

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            user = form.get_user()
            if user:
                token = generate_jwt_token(user)
                response.set_cookie(
                    key='jwt_token',
                    value=token,
                    httponly=True,
                    samesite='Lax',
                    max_age=8 * 3600,
                    secure=settings.SESSION_COOKIE_SECURE,
                )
            return response
        except Exception:
            return render(self.request, self.template_name, {'form': form})

    def form_invalid(self, form):
        try:
            if not getattr(self.request, '_login_attempt_logged', False):
                registrar_intento_acceso(
                    self.request,
                    nombre_usuario=self.request.POST.get('username', ''),
                    exitoso=False,
                )
            return super().form_invalid(form)
        except Exception:
            return render(self.request, self.template_name, {'form': form})


@require_http_methods(['POST'])
def login_user_lookup(request):
    username = request.POST.get('username', '').strip()
    if not username:
        return JsonResponse({'success': False})

    user = User.objects.filter(username__iexact=username, is_active=True).only(
        'first_name', 'last_name',
    ).first()
    full_name = user.get_full_name().strip() if user else ''
    response = JsonResponse({
        'success': bool(full_name),
        'nombre': full_name,
    })
    response['Cache-Control'] = 'no-store'
    return response


@require_http_methods(['GET', 'POST'])
def change_password(request):
    username = ''
    errors = []

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        authentication_form = CustomAuthenticationForm(
            request,
            data={'username': username, 'password': current_password},
        )
        credentials_valid = authentication_form.is_valid()
        if not credentials_valid:
            for field_errors in authentication_form.errors.values():
                errors.extend(str(error) for error in field_errors)

        if not new_password:
            errors.append('Escribe una nueva contraseña.')
        if not confirm_password:
            errors.append('Confirma la nueva contraseña.')
        elif new_password != confirm_password:
            errors.append('Las contraseñas nuevas no coinciden.')

        if credentials_valid and new_password and new_password == confirm_password:
            user = authentication_form.get_user()
            if user.check_password(new_password):
                errors.append('La nueva contraseña debe ser diferente a la contraseña actual.')
            else:
                try:
                    validate_password(new_password, user=user)
                except ValidationError as error:
                    errors.extend(error.messages)

        if not errors:
            user = authentication_form.get_user()
            with transaction.atomic(using='default'):
                user.set_password(new_password)
                user.save(using='default', update_fields=['password'])
            logout(request)
            response = render(
                request,
                'registration/password_change.html',
                {'password_changed': True},
            )
            response.delete_cookie('jwt_token')
            return response

    return render(request, 'registration/password_change.html', {
        'username': username,
        'errors': errors,
        'password_changed': False,
    })


# Verifica si un usuario tiene permisos de administrador.
# Un usuario administrador debe estar activo, autenticado y ser superusuario o pertenecer al grupo Admin.
def usuario_es_admin(usuario):
    return usuario is not None and usuario.is_authenticated and usuario.is_active and (
        usuario.is_superuser or usuario.groups.filter(name='Admin').exists()
    )


# Endpoint de autenticación para el modal de cambio de usuario / AJAX login.
# Recibe JSON con credenciales y devuelve resultado de inicio de sesión.
@require_http_methods(['POST'])
def ajax_login(request):
    data = request.POST
    if request.content_type and 'application/json' in request.content_type:
        try:
            data = json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'JSON inválido.'}, status=400)

    username = data.get('username', '').strip() if hasattr(data, 'get') else ''
    password = data.get('password', '') if hasattr(data, 'get') else ''

    if not username or not password:
        return JsonResponse({'success': False, 'error': 'Debes ingresar usuario y contraseña.'}, status=400)

    form = CustomAuthenticationForm(request, data={'username': username, 'password': password})
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        token = generate_jwt_token(user)
        response = JsonResponse({'success': True})
        response.set_cookie(
            key='jwt_token',
            value=token,
            httponly=True,
            samesite='Lax',
            max_age=8 * 3600,
            secure=settings.SESSION_COOKIE_SECURE,
        )
        return response
    else:
        error_msg = 'Usuario o contraseña incorrectos.'
        if form.non_field_errors():
            error_msg = form.non_field_errors()[0]
        elif form.errors:
            for field, errors in form.errors.items():
                if errors:
                    error_msg = errors[0]
                    break
        return JsonResponse({'success': False, 'error': str(error_msg)}, status=401)



# Vista para el registro de nuevos usuarios desde el panel administrativo.
# Crea usuarios y perfiles asociados, y genera credenciales.
@login_required
def signup(request):
    if not usuario_es_admin(request.user):
        return redirect('modulos')

    mensaje = ''

    created_username = ''
    created_password = ''
    show_modal = False

    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            puesto = form.cleaned_data['puesto']
            rol = form.cleaned_data['rol']
            password = form.cleaned_data['password1']
            username = form.cleaned_data['username']

            # Validación: evitar duplicidad de usuarios.
            # Si el username ya existe, devolver error y no crear usuario.
            if User.objects.filter(username=username).exists():
                form.add_error('username', 'Usuario ya existe. Elige otro nombre o verifica el usuario.')
                return render(request, 'registration/signup.html', {
                    'form': form,
                    'mensaje': mensaje,
                    'created_username': created_username,
                    'created_password': created_password,
                    'show_modal': show_modal,
                })

            name_parts = full_name.strip().split()
            first_name = name_parts[0] if name_parts else ''
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

            usuario = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )

            if isinstance(rol, Group):
                usuario.groups.add(rol)
            elif rol:
                group, _ = Group.objects.get_or_create(name=str(rol))
                usuario.groups.add(group)
            usuario.save()

            UserProfile.objects.create(
                usuario=usuario,
                codigo=username,
                puesto=puesto
            )

            if not request.user.is_authenticated:
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('modulos')

            mensaje = f'Usuario creado con éxito. Nombre de usuario: {username}'
            created_username = username
            created_password = password
            show_modal = True
            form = AdminUserCreationForm()
    else:
        form = AdminUserCreationForm()

    return render(request, 'registration/signup.html', {
        'form': form,
        'mensaje': mensaje,
        'created_username': created_username,
        'created_password': created_password,
        'show_modal': show_modal,
    })


# Busca un usuario o empleado por código para completar formularios.
# Esta vista devuelve información útil para autocompletar campos en el frontend.
@login_required
@require_http_methods(["GET"])
def buscar_usuario_por_codigo(request):
    if not usuario_es_admin(request.user):
        return JsonResponse({'error': 'No autorizado.'}, status=403)

    codigo = request.GET.get('codigo', '').strip()

    if not codigo:
        return JsonResponse({'error': 'Código requerido'}, status=400)

    try:
        empleado = Empleado.objects.filter(puesto__iexact=codigo).first()

        if not empleado:
            return JsonResponse({'success': False, 'error': 'Empleado no encontrado en el catálogo'}, status=404)

        return JsonResponse({
            'success': True,
            'nombre': ' '.join(filter(None, [empleado.empleado, empleado.segundo_apellido])),
            'puesto': empleado.nombre_puesto,
            'codigo': empleado.puesto,
            'area': empleado.empresa,
            'email': '',
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# Administra el estado de usuarios desde la interfaz administrativa.
# Permite activar/desactivar o eliminar usuarios según permisos administrativos.
@login_required
@require_http_methods(["POST"])
def api_usuario(request, user_id):
    try:
        usuario = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

    if usuario == request.user:
        return JsonResponse({'error': 'No puedes modificar tu propio usuario aquí.'}, status=400)

    if not usuario_es_admin(request.user):
        return JsonResponse({'error': 'No autorizado.'}, status=403)

    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    action = data.get('action')
    if action == 'toggle_estado':
        if usuario.groups.filter(name='Admin').exists() or usuario.is_superuser:
            return JsonResponse({'error': 'No se puede bloquear a un usuario administrador.'}, status=403)
        if not usuario.groups.filter(name='Usuario').exists():
            return JsonResponse({'error': 'Solo se pueden bloquear usuarios con rol de Usuario.'}, status=403)
        usuario.is_active = not usuario.is_active
        usuario.save()
        if usuario.is_active:
            lockout_window = getattr(settings, 'LOGIN_RATE_LIMIT_LOCKOUT_SECONDS', 300)
            recent_attempts = LoginAttempt.objects.filter(
                username_attempt__iexact=usuario.username,
                successful=False,
                created_at__gte=timezone.now() - timedelta(seconds=lockout_window),
                ip_address__isnull=False,
            ).values_list('ip_address', flat=True).distinct()
            normalized_username = usuario.username.strip().lower()
            for ip_address in recent_attempts:
                cache.delete(f'login_attempts:{ip_address}:{normalized_username}')
        return JsonResponse({'success': True, 'activo': usuario.is_active})

    if action == 'delete':
        username = usuario.username
        usuario.delete()
        return JsonResponse({'success': True, 'message': f'Usuario {username} eliminado correctamente.'})

    return JsonResponse({'error': 'Acción no válida'}, status=400)


@login_required
@require_http_methods(['POST'])
def reset_user_password(request, user_id):
    if not usuario_es_admin(request.user):
        return JsonResponse({'success': False, 'error': 'No autorizado.'}, status=403)

    try:
        data = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Solicitud inválida.'}, status=400)

    if not isinstance(data, dict):
        return JsonResponse({'success': False, 'error': 'Solicitud inválida.'}, status=400)

    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')
    if not isinstance(new_password, str) or not isinstance(confirm_password, str):
        return JsonResponse({'success': False, 'error': 'Las contraseñas deben ser texto.'}, status=400)
    if not new_password or not confirm_password:
        return JsonResponse({'success': False, 'error': 'Completa y confirma la nueva contraseña.'}, status=400)
    if new_password != confirm_password:
        return JsonResponse({'success': False, 'error': 'Las contraseñas no coinciden.'}, status=400)

    try:
        target_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Usuario no encontrado.'}, status=404)

    if target_user.is_superuser or target_user.groups.filter(name='Admin').exists():
        return JsonResponse({'success': False, 'error': 'Solo se pueden restablecer contraseñas del rol Usuario.'}, status=403)
    if not target_user.groups.filter(name='Usuario').exists():
        return JsonResponse({'success': False, 'error': 'La cuenta seleccionada no pertenece al rol Usuario.'}, status=403)

    try:
        validate_password(new_password, user=target_user)
    except ValidationError as error:
        return JsonResponse({'success': False, 'error': ' '.join(error.messages)}, status=400)

    with transaction.atomic(using='default'):
        target_user.set_password(new_password)
        target_user.save(using='default', update_fields=['password'])

    logger.info(
        'Admin usuario_id=%s restableció la contraseña de usuario_id=%s.',
        request.user.pk,
        target_user.pk,
    )
    return JsonResponse({'success': True, 'message': 'Contraseña restablecida correctamente.'})


# ==================== API PROVEEDORES ====================
@login_required
@require_http_methods(["GET", "POST"])
def api_proveedores(request):
    if request.method == 'GET':
        proveedores = Proveedor.objects.all().values()
        return JsonResponse(list(proveedores), safe=False)

    elif request.method == 'POST':
        if not usuario_es_admin(request.user):
            return JsonResponse({'error': 'No autorizado.'}, status=403)
        try:
            data = json.loads(request.body)
            data = normalizar_datos(data)
            if not data.get('codigo') or not data.get('nit') or not data.get('razonSocial'):
                return JsonResponse({'error': 'Faltan campos requeridos'}, status=400)
            dias_credito = data.get('diasCredito', '')
            dias_credito = int(dias_credito) if dias_credito and dias_credito.strip() else 0
            proveedor = Proveedor.objects.create(
                codigo=data.get('codigo'),
                nit=data.get('nit'),
                razon_social=data.get('razonSocial'),
                nombre_propietario=data.get('nombrePropietario', ''),
                regimen_tributario=data.get('regimenTributario', ''),
                tipo_factura=data.get('tipoFactura', ''),
                dias_credito=dias_credito
            )
            return JsonResponse({'success': True, 'message': 'Proveedor creado correctamente', 'id': proveedor.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["PUT", "DELETE"])
def api_proveedor_detalle(request, proveedor_id):
    try:
        proveedor = Proveedor.objects.get(id=proveedor_id)
    except Proveedor.DoesNotExist:
        return JsonResponse({'error': 'Proveedor no encontrado'}, status=404)

    if request.method == 'PUT':
        if not usuario_es_admin(request.user):
            return JsonResponse({'error': 'No autorizado.'}, status=403)
        try:
            data = json.loads(request.body)
            data = normalizar_datos(data)
            proveedor.codigo = data.get('codigo', proveedor.codigo)
            proveedor.nit = data.get('nit', proveedor.nit)
            proveedor.razon_social = data.get('razonSocial', proveedor.razon_social)
            proveedor.nombre_propietario = data.get('nombrePropietario', proveedor.nombre_propietario)
            proveedor.regimen_tributario = data.get('regimenTributario', proveedor.regimen_tributario)
            proveedor.tipo_factura = data.get('tipoFactura', proveedor.tipo_factura)
            dias_credito = data.get('diasCredito', proveedor.dias_credito)
            proveedor.dias_credito = int(dias_credito) if dias_credito and str(dias_credito).strip() else proveedor.dias_credito
            proveedor.save()
            return JsonResponse({'success': True, 'message': 'Proveedor actualizado correctamente'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'DELETE':
        if not usuario_es_admin(request.user):
            return JsonResponse({'error': 'No autorizado.'}, status=403)
        proveedor.delete()
        return JsonResponse({'success': True, 'message': 'Proveedor eliminado correctamente'})


# ==================== API EMPLEADOS ====================
@login_required
@require_http_methods(["GET", "POST"])
def api_empleados(request):
    if request.method == 'GET':
        empleados = Empleado.objects.all()
        if usuario_es_admin(request.user):
            empleados = empleados.values()
        else:
            empleados = empleados.values(
                'id', 'empresa', 'empleado', 'segundo_apellido', 'puesto', 'nombre_puesto',
            )
        return JsonResponse(list(empleados), safe=False)

    elif request.method == 'POST':
        if not usuario_es_admin(request.user):
            return JsonResponse({'error': 'No autorizado.'}, status=403)
        try:
            data = json.loads(request.body)
            data = normalizar_datos(data)
            no_cui = str(data.get('no_cui', '')).strip()
            if not data.get('empresa') or not data.get('empleado') or not data.get('segundo_apellido', '').strip() or not no_cui or not str(data.get('puesto', '')).strip():
                return JsonResponse({'error': 'Faltan campos requeridos'}, status=400)
            if not re.fullmatch(r'\d{1,13}', no_cui):
                return JsonResponse({'error': 'El No. CUI debe contener únicamente dígitos y no superar 13 caracteres'}, status=400)
            codigo = str(data.get('puesto', '')).strip()
            if Empleado.objects.filter(puesto=codigo).exists():
                return JsonResponse({'error': 'Ese código ya fue registrado'}, status=400)
            empleado = Empleado.objects.create(
                empresa=data.get('empresa'),
                empleado=data.get('empleado'),
                segundo_apellido=data['segundo_apellido'].strip(),
                no_cui=no_cui,
                puesto=codigo,
                nombre_puesto=data.get('nombre_puesto', '')
            )
            return JsonResponse({'success': True, 'message': 'Empleado creado correctamente', 'id': empleado.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["PUT", "DELETE"])
def api_empleado_detalle(request, empleado_id):
    try:
        empleado = Empleado.objects.get(id=empleado_id)
    except Empleado.DoesNotExist:
        return JsonResponse({'error': 'Empleado no encontrado'}, status=404)

    if request.method == 'PUT':
        if not usuario_es_admin(request.user):
            return JsonResponse({'error': 'No autorizado.'}, status=403)
        try:
            data = json.loads(request.body)
            data = normalizar_datos(data)
            empleado.empresa = data.get('empresa', empleado.empresa)
            empleado.empleado = data.get('empleado', empleado.empleado)
            if 'segundo_apellido' in data:
                segundo_apellido = data['segundo_apellido'].strip()
                if not segundo_apellido:
                    return JsonResponse({'error': 'El segundo apellido es obligatorio'}, status=400)
                empleado.segundo_apellido = segundo_apellido
            if 'no_cui' in data:
                no_cui = str(data['no_cui']).strip()
                if not re.fullmatch(r'\d{1,13}', no_cui):
                    return JsonResponse({'error': 'El No. CUI debe contener únicamente dígitos y no superar 13 caracteres'}, status=400)
                empleado.no_cui = no_cui
            if 'puesto' in data:
                codigo = str(data['puesto']).strip()
                if Empleado.objects.filter(puesto=codigo).exclude(id=empleado.id).exists():
                    return JsonResponse({'error': 'Ese código ya fue registrado'}, status=400)
                empleado.puesto = codigo
            empleado.nombre_puesto = data.get('nombre_puesto', empleado.nombre_puesto)
            empleado.save()
            return JsonResponse({'success': True, 'message': 'Empleado actualizado correctamente'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'DELETE':
        if not usuario_es_admin(request.user):
            return JsonResponse({'error': 'No autorizado.'}, status=403)
        empleado.delete()
        return JsonResponse({'success': True, 'message': 'Empleado eliminado correctamente'})


# ==================== API MAQUINARIA ====================
@login_required
@require_http_methods(["GET", "POST"])
def api_maquinaria(request):
    if request.method == 'GET':
        maquinaria = Maquinaria.objects.all().values()
        return JsonResponse(list(maquinaria), safe=False)

    elif request.method == 'POST':
        if not usuario_es_admin(request.user):
            return JsonResponse({'error': 'No autorizado.'}, status=403)
        try:
            data = json.loads(request.body)
            if not data.get('codigo_maquina') or not data.get('tipo_maquina'):
                return JsonResponse({'error': 'Faltan campos requeridos'}, status=400)
            maquinaria = Maquinaria.objects.create(
                codigo_maquina=data.get('codigo_maquina'),
                combustible=data.get('combustible', ''),
                id_proveedor=data.get('id_proveedor', ''),
                tipo_maquina=data.get('tipo_maquina'),
                marca_maquina=data.get('marca_maquina', ''),
                serie_maquina=data.get('serie_maquina', ''),
                placa_matricula=data.get('placa_matricula', ''),
                observaciones=data.get('observaciones', '')
            )
            return JsonResponse({'success': True, 'message': 'Máquina creada correctamente', 'id': maquinaria.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["PUT", "DELETE"])
def api_maquinaria_detalle(request, maquinaria_id):
    try:
        maquinaria = Maquinaria.objects.get(id=maquinaria_id)
    except Maquinaria.DoesNotExist:
        return JsonResponse({'error': 'Máquina no encontrada'}, status=404)

    if request.method == 'PUT':
        if not usuario_es_admin(request.user):
            return JsonResponse({'error': 'No autorizado.'}, status=403)
        try:
            data = json.loads(request.body)
            maquinaria.codigo_maquina = data.get('codigo_maquina', maquinaria.codigo_maquina)
            maquinaria.combustible = data.get('combustible', maquinaria.combustible)
            maquinaria.id_proveedor = data.get('id_proveedor', maquinaria.id_proveedor)
            maquinaria.tipo_maquina = data.get('tipo_maquina', maquinaria.tipo_maquina)
            maquinaria.marca_maquina = data.get('marca_maquina', maquinaria.marca_maquina)
            maquinaria.serie_maquina = data.get('serie_maquina', maquinaria.serie_maquina)
            maquinaria.placa_matricula = data.get('placa_matricula', maquinaria.placa_matricula)
            maquinaria.observaciones = data.get('observaciones', maquinaria.observaciones)
            maquinaria.save()
            return JsonResponse({'success': True, 'message': 'Máquina actualizada correctamente'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'DELETE':
        if not usuario_es_admin(request.user):
            return JsonResponse({'error': 'No autorizado.'}, status=403)
        maquinaria.delete()
        return JsonResponse({'success': True, 'message': 'Máquina eliminada correctamente'})


# ==================== API BODEGAS ====================
@login_required
@require_http_methods(["GET", "POST"])
def api_bodegas(request):
    if request.method == 'GET':
        bodegas = Bodega.objects.all().values()
        return JsonResponse(list(bodegas), safe=False)

    elif request.method == 'POST':
        if not usuario_es_admin(request.user):
            return JsonResponse({'error': 'No autorizado.'}, status=403)
        try:
            data = json.loads(request.body)
            if not data.get('codigo') or not data.get('nombre_bodega'):
                return JsonResponse({'error': 'Faltan campos requeridos'}, status=400)
            bodega = Bodega.objects.create(
                codigo=data.get('codigo'),
                nombre_bodega=data.get('nombre_bodega'),
                unidad_medida=data.get('unidad_medida', ''),
                capacidad=data.get('capacidad', ''),
                observaciones=data.get('observaciones', '')
            )
            return JsonResponse({'success': True, 'message': 'Bodega creada correctamente', 'id': bodega.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["PUT", "DELETE"])
def api_bodega_detalle(request, bodega_id):
    try:
        bodega = Bodega.objects.get(id=bodega_id)
    except Bodega.DoesNotExist:
        return JsonResponse({'error': 'Bodega no encontrada'}, status=404)

    if request.method == 'PUT':
        if not usuario_es_admin(request.user):
            return JsonResponse({'error': 'No autorizado.'}, status=403)
        try:
            data = json.loads(request.body)
            bodega.codigo = data.get('codigo', bodega.codigo)
            bodega.nombre_bodega = data.get('nombre_bodega', bodega.nombre_bodega)
            bodega.unidad_medida = data.get('unidad_medida', bodega.unidad_medida)
            bodega.capacidad = data.get('capacidad', bodega.capacidad)
            bodega.observaciones = data.get('observaciones', bodega.observaciones)
            bodega.save()
            return JsonResponse({'success': True, 'message': 'Bodega actualizada correctamente'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'DELETE':
        if not usuario_es_admin(request.user):
            return JsonResponse({'error': 'No autorizado.'}, status=403)
        bodega.delete()
        return JsonResponse({'success': True, 'message': 'Bodega eliminada correctamente'})


# ==================== API ARTICULOS ====================
@login_required
@require_http_methods(["GET", "POST"])
def api_articulos(request):
    if request.method == 'GET':
        articulos = Articulo.objects.all().values()
        return JsonResponse(list(articulos), safe=False)

    elif request.method == 'POST':
        if not usuario_es_admin(request.user):
            return JsonResponse({'error': 'No autorizado.'}, status=403)
        try:
            data = json.loads(request.body)
            if not data.get('codigo_articulo') or not data.get('descripcion'):
                return JsonResponse({'error': 'Faltan campos requeridos'}, status=400)
            articulo = Articulo.objects.create(
                codigo_articulo=data.get('codigo_articulo'),
                descripcion=data.get('descripcion'),
                unidad_medida=data.get('unidad_medida', ''),
                categoria=data.get('categoria', ''),
                stock=data.get('stock', 0)
            )
            return JsonResponse({'success': True, 'message': 'Artículo creado correctamente', 'id': articulo.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["PUT", "DELETE"])
def api_articulo_detalle(request, articulo_id):
    try:
        articulo = Articulo.objects.get(id=articulo_id)
    except Articulo.DoesNotExist:
        return JsonResponse({'error': 'Artículo no encontrado'}, status=404)

    if request.method == 'PUT':
        if not usuario_es_admin(request.user):
            return JsonResponse({'error': 'No autorizado.'}, status=403)
        try:
            data = json.loads(request.body)
            articulo.codigo_articulo = data.get('codigo_articulo', articulo.codigo_articulo)
            articulo.descripcion = data.get('descripcion', articulo.descripcion)
            articulo.unidad_medida = data.get('unidad_medida', articulo.unidad_medida)
            articulo.categoria = data.get('categoria', articulo.categoria)
            articulo.stock = data.get('stock', articulo.stock)
            articulo.save()
            return JsonResponse({'success': True, 'message': 'Artículo actualizado correctamente'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'DELETE':
        if not usuario_es_admin(request.user):
            return JsonResponse({'error': 'No autorizado.'}, status=403)
        articulo.delete()
        return JsonResponse({'success': True, 'message': 'Artículo eliminado correctamente'})


# ==================== API CATÁLOGOS AUXILIARES ====================
# Helper genérico para catálogos simples (código + descripción/nombre)
def _api_catalogo_list_create(request, ModelClass, required_fields, create_fn):
    if request.method == 'GET':
        items = list(ModelClass.objects.all().values())
        return JsonResponse(items, safe=False)

    if not usuario_es_admin(request.user):
        return JsonResponse({'error': 'No autorizado.'}, status=403)

    try:
        data = json.loads(request.body)
        data = normalizar_datos(data)
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'Campo requerido: {field}'}, status=400)
        obj = create_fn(data)
        return JsonResponse({'success': True, 'id': obj.id}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def _api_catalogo_detail(request, ModelClass, obj_id, update_fn, nombre='Registro'):
    try:
        obj = ModelClass.objects.get(id=obj_id)
    except ModelClass.DoesNotExist:
        return JsonResponse({'error': f'{nombre} no encontrado'}, status=404)

    if request.method == 'PUT':
        if not usuario_es_admin(request.user):
            return JsonResponse({'error': 'No autorizado.'}, status=403)
        try:
            data = json.loads(request.body)
            data = normalizar_datos(data)
            update_fn(obj, data)
            obj.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    elif request.method == 'DELETE':
        if not usuario_es_admin(request.user):
            return JsonResponse({'error': 'No autorizado.'}, status=403)
        obj.delete()
        return JsonResponse({'success': True})


# --- LABORES ---
def _normalizar_proceso_labor(valor):
    proceso = str(valor or '').strip().casefold()
    if proceso not in dict(Labor.PROCESO_CHOICES):
        raise ValueError('Selecciona Siembras, Fertilización o Riego.')
    return proceso


def _validar_proceso_cuenta(valor, cuenta_actual=None):
    proceso = str(valor or '').strip().casefold()
    etiquetas = dict(Labor.PROCESO_CHOICES)
    if proceso not in etiquetas:
        raise ValueError('Selecciona Siembras, Fertilización o Riego.')
    cuentas_proceso = Cuenta.objects.filter(proceso=proceso)
    if cuenta_actual is not None:
        cuentas_proceso = cuentas_proceso.exclude(pk=cuenta_actual.pk)
    if cuentas_proceso.exists():
        raise ValueError(f"Ya existe una cuenta para el proceso {etiquetas[proceso]}.")
    return proceso


def _validar_codigo_cuenta(valor):
    codigo = str(valor or '').strip()
    if not re.fullmatch(r'[0-9]{12}', codigo):
        raise ValueError('El código de cuenta debe contener exactamente 12 dígitos.')
    return codigo


@login_required
@require_http_methods(["GET", "POST"])
def api_labores(request):
    def crear_labor(data):
        return Labor.objects.create(
            codigo=data['codigo'],
            descripcion=data['descripcion'],
            proceso=_normalizar_proceso_labor(data.get('proceso')),
        )

    return _api_catalogo_list_create(
        request, Labor, ['codigo', 'descripcion', 'proceso'], crear_labor
    )

@login_required
@require_http_methods(["PUT", "DELETE"])
def api_labor_detalle(request, pk):
    def upd(obj, d):
        obj.codigo = d.get('codigo', obj.codigo)
        obj.descripcion = d.get('descripcion', obj.descripcion)
        if 'proceso' in d:
            obj.proceso = _normalizar_proceso_labor(d['proceso'])
    return _api_catalogo_detail(request, Labor, pk, upd, 'Labor')


# --- CUENTAS ---
@login_required
@require_http_methods(["GET", "POST"])
def api_cuentas(request):
    def crear_cuenta(data):
        codigo = _validar_codigo_cuenta(data.get('codigo'))
        proceso = _validar_proceso_cuenta(data.get('proceso'))
        return Cuenta.objects.create(
            codigo=codigo,
            descripcion=data['descripcion'],
            tipo=data.get('tipo', ''),
            proceso=proceso,
        )

    return _api_catalogo_list_create(
        request, Cuenta, ['codigo', 'descripcion', 'proceso', 'tipo'], crear_cuenta
    )

@login_required
@require_http_methods(["PUT", "DELETE"])
def api_cuenta_detalle(request, pk):
    def upd(obj, d):
        obj.codigo = _validar_codigo_cuenta(d.get('codigo', obj.codigo))
        obj.descripcion = d.get('descripcion', obj.descripcion)
        tipo = d.get('tipo', obj.tipo)
        if not str(tipo or '').strip():
            raise ValueError('Campo requerido: tipo')
        obj.tipo = tipo
        obj.proceso = _validar_proceso_cuenta(d.get('proceso', obj.proceso), obj)
    return _api_catalogo_detail(request, Cuenta, pk, upd, 'Cuenta')


# --- UNIDADES DE MEDIDA ---
@login_required
@require_http_methods(["GET", "POST"])
def api_unidades(request):
    return _api_catalogo_list_create(
        request, UnidadMedida, ['codigo', 'descripcion'],
        lambda d: UnidadMedida.objects.create(codigo=d['codigo'], descripcion=d['descripcion'])
    )

@login_required
@require_http_methods(["PUT", "DELETE"])
def api_unidad_detalle(request, pk):
    def upd(obj, d):
        obj.codigo = d.get('codigo', obj.codigo)
        obj.descripcion = d.get('descripcion', obj.descripcion)
    return _api_catalogo_detail(request, UnidadMedida, pk, upd, 'Unidad de Medida')


# --- NOMBRES DE PUESTO ---
@login_required
@require_http_methods(["GET", "POST"])
def api_nombres_puesto(request):
    return _api_catalogo_list_create(
        request, NombrePuesto, ['nombre'],
        lambda d: NombrePuesto.objects.create(nombre=d['nombre'].strip())
    )


@login_required
@require_http_methods(["PUT", "DELETE"])
def api_nombre_puesto_detalle(request, pk):
    def upd(obj, d):
        obj.nombre = d.get('nombre', obj.nombre).strip()
    return _api_catalogo_detail(request, NombrePuesto, pk, upd, 'Nombre de puesto')


# --- VARIEDADES ---
@login_required
@require_http_methods(["GET", "POST"])
def api_variedades(request):
    return _api_catalogo_list_create(
        request, Variedad, ['codigo', 'descripcion'],
        lambda d: Variedad.objects.create(codigo=d['codigo'], descripcion=d['descripcion'])
    )

@login_required
@require_http_methods(["PUT", "DELETE"])
def api_variedad_detalle(request, pk):
    def upd(obj, d):
        obj.codigo = d.get('codigo', obj.codigo)
        obj.descripcion = d.get('descripcion', obj.descripcion)
    return _api_catalogo_detail(request, Variedad, pk, upd, 'Variedad')


# --- TIPOS DE MÁQUINA ---
@login_required
@require_http_methods(["GET", "POST"])
def api_tipos_maquina(request):
    return _api_catalogo_list_create(
        request, TipoMaquina, ['codigo', 'descripcion'],
        lambda d: TipoMaquina.objects.create(codigo=d['codigo'], descripcion=d['descripcion'])
    )

@login_required
@require_http_methods(["PUT", "DELETE"])
def api_tipo_maquina_detalle(request, pk):
    def upd(obj, d):
        obj.codigo = d.get('codigo', obj.codigo)
        obj.descripcion = d.get('descripcion', obj.descripcion)
    return _api_catalogo_detail(request, TipoMaquina, pk, upd, 'Tipo de Máquina')


# --- MARCAS ---
@login_required
@require_http_methods(["GET", "POST"])
def api_marcas(request):
    return _api_catalogo_list_create(
        request, Marca, ['codigo', 'descripcion'],
        lambda d: Marca.objects.create(codigo=d['codigo'], descripcion=d['descripcion'])
    )

@login_required
@require_http_methods(["PUT", "DELETE"])
def api_marca_detalle(request, pk):
    def upd(obj, d):
        obj.codigo = d.get('codigo', obj.codigo)
        obj.descripcion = d.get('descripcion', obj.descripcion)
    return _api_catalogo_detail(request, Marca, pk, upd, 'Marca')


# --- MUNICIPIOS ---
@login_required
@require_http_methods(["GET", "POST"])
def api_municipios(request):
    return _api_catalogo_list_create(
        request, Municipio, ['codigo', 'nombre'],
        lambda d: Municipio.objects.create(codigo=d['codigo'], nombre=d['nombre'], departamento=d.get('departamento', ''))
    )

@login_required
@require_http_methods(["PUT", "DELETE"])
def api_municipio_detalle(request, pk):
    def upd(obj, d):
        obj.codigo = d.get('codigo', obj.codigo)
        obj.nombre = d.get('nombre', obj.nombre)
        obj.departamento = d.get('departamento', obj.departamento)
    return _api_catalogo_detail(request, Municipio, pk, upd, 'Municipio')


# --- AUXILIARES ---
@login_required
@require_http_methods(["GET", "POST"])
def api_auxiliares(request):
    return _api_catalogo_list_create(
        request, Auxiliar, ['codigo', 'nombre'],
        lambda d: Auxiliar.objects.create(codigo=d['codigo'], nombre=d['nombre'], tipo=d.get('tipo', ''))
    )

@login_required
@require_http_methods(["PUT", "DELETE"])
def api_auxiliar_detalle(request, pk):
    def upd(obj, d):
        obj.codigo = d.get('codigo', obj.codigo)
        obj.nombre = d.get('nombre', obj.nombre)
        obj.tipo = d.get('tipo', obj.tipo)
    return _api_catalogo_detail(request, Auxiliar, pk, upd, 'Auxiliar')
