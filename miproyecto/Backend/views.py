import json
from decimal import Decimal, InvalidOperation
import unicodedata

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum

# Vistas principales del sistema agrícola y de administración.
# Aquí se gestionan las páginas de acceso, módulos, registros operativos,
# edición y eliminación, así como el control de permisos para cada usuario.

from django.core.exceptions import ValidationError
from accounts.forms import AdminUserCreationForm
from accounts.validators import PasswordStandardValidator
from accounts.models import (
    Articulo, Empleado, UserProfile, RegistroOperativo, Proveedor, Maquinaria, Auxiliar, Cuenta,
    Labor, Variedad, Municipio, ProgramacionOperacion, FirmaAutorizada,
    DespachoCombustible, SecuenciaDespacho, TanqueCombustible, OrdenMantenimiento,
    ControlServicioHorometro, DisponibilidadMaquinaria, normalizar_texto
)


# Determina si un usuario tiene permisos administrativos.
def user_is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='Admin').exists())

# Determina si un usuario pertenece a un rol permitido para operar el sistema.
def user_is_user_or_admin(user):
    return user.is_authenticated and (
        user_is_admin(user) or user.groups.filter(name='Usuario').exists()
    )


def home(request):
    """Redirige al usuario siempre al login.

    La URL raíz debe abrir la pantalla de inicio de sesión, incluso si ya está autenticado.
    """
    return redirect('login')


@login_required
def modulos(request):
    """Renderiza la pantalla de módulos con visibilidad condicional según el rol."""
    try:
        return render(request, 'modulos.html', {
            'is_admin': user_is_admin(request.user)
        })
    except Exception:
        return render(request, 'modulos.html', {
            'is_admin': user_is_admin(request.user),
            'request': request,
            'messages': [],
        })


@login_required
def configuracion_catalogos(request):
    """Muestra la página de configuración y catálogos para el usuario autenticado."""
    return render(request, 'configuracion_catalogos.html', {
        'is_admin': user_is_admin(request.user)
    })


@login_required
def datos_registrados(request):
    """Muestra en una pantalla independiente los datos guardados en catálogos."""
    return render(request, 'datos_registrados.html', {
        'is_admin': user_is_admin(request.user)
    })


def to_title_case(val):
    return normalizar_texto(val)


def _normalizar_tipo_servicio(tipo_servicio):
    normalizado = unicodedata.normalize('NFKD', tipo_servicio or '')
    normalizado = normalizado.encode('ascii', 'ignore').decode('ascii').casefold()
    return ' '.join(normalizado.split())


def _es_servicio_envio_semilla(tipo_servicio):
    return _normalizar_tipo_servicio(tipo_servicio) == 'envio de semilla de cana'


def _es_servicio_transporte(tipo_servicio):
    return _normalizar_tipo_servicio(tipo_servicio) in {
        'envio de semilla de cana',
        'transporte de personal',
        'viajes de material o maquinaria',
    }


def _catalogos_registro_operativo():
    return {
        'proveedores': Proveedor.objects.all().order_by('razon_social'),
        'maquinarias': Maquinaria.objects.all().order_by('codigo_maquina'),
        'fincas': Auxiliar.objects.filter(tipo__icontains='finca').order_by('nombre'),
        'labores': Labor.objects.all().order_by('proceso', 'codigo'),
        'procesos_labores': Labor.PROCESO_CHOICES,
        'cuentas_por_proceso': dict(Cuenta.objects.values_list('proceso', 'codigo')),
        'variedades': Variedad.objects.all().order_by('descripcion'),
        'municipios': Municipio.objects.all().order_by('nombre'),
    }


@login_required
@require_http_methods(['GET', 'POST'])
def firmas_autorizadas(request):
    if not user_is_admin(request.user):
        messages.warning(request, 'No tienes permisos para acceder a este módulo.')
        return redirect('modulos')

    form_data = {'codigo': '', 'nombre': '', 'puesto': '', 'area': ''}
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()
        empleado = Empleado.objects.filter(puesto__iexact=codigo).first() if codigo else None

        if not codigo:
            messages.error(request, 'Escribe el código del empleado.')
        elif not empleado:
            messages.error(request, 'No se encontró un empleado con ese código.')
            form_data['codigo'] = codigo
        elif FirmaAutorizada.objects.filter(codigo__iexact=empleado.puesto).exists():
            messages.error(request, 'Ya existe una firma autorizada con ese código.')
            form_data = {
                'codigo': empleado.puesto,
                'nombre': to_title_case(' '.join(filter(None, [empleado.empleado, empleado.segundo_apellido]))),
                'puesto': to_title_case(empleado.nombre_puesto),
                'area': to_title_case(empleado.empresa),
            }
        else:
            FirmaAutorizada.objects.create(
                codigo=empleado.puesto,
                nombre=to_title_case(' '.join(filter(None, [empleado.empleado, empleado.segundo_apellido]))),
                puesto=to_title_case(empleado.nombre_puesto),
                area=to_title_case(empleado.empresa),
            )
            messages.success(request, 'Firma autorizada registrada correctamente.')
            return redirect('firmas_autorizadas')

    return render(request, 'firmas_autorizadas.html', {
        'firmas': FirmaAutorizada.objects.all(),
        'form_data': form_data,
    })


@login_required
def registros_operativos(request):
    if not user_is_user_or_admin(request.user):
        messages.warning(request, 'No tienes permisos para acceder a este módulo.')
        return redirect('modulos')
    if request.method == 'POST':
        tipo_servicio = to_title_case(request.POST.get('tipo_servicio', ''))
        es_envio_semilla = _es_servicio_envio_semilla(tipo_servicio)
        es_transporte = _es_servicio_transporte(tipo_servicio)
        corte_semilla = request.POST.get('corte_semilla', '').strip() or None
        if not es_envio_semilla:
            corte_semilla = None

        finca_corte_semilla = None
        lote_corte_semilla = None
        if es_envio_semilla and corte_semilla == '1':
            finca_corte_semilla = request.POST.get('finca_corte_semilla', '').strip()
            lote_corte_semilla = request.POST.get('lote_corte_semilla', '').strip()
            if not finca_corte_semilla or not lote_corte_semilla:
                messages.error(request, 'Indica la finca y el lote donde se cortó la semilla.')
                return redirect('registros')

        area_lote_raw = request.POST.get('area_lote', '').strip()
        try:
            area_lote = Decimal(area_lote_raw) if area_lote_raw else None
        except InvalidOperation:
            messages.error(request, 'El área del lote debe ser un número válido y no puede superar 150 hectáreas.')
            return redirect('registros')

        if area_lote is not None and (not area_lote.is_finite() or area_lote > Decimal('150')):
            messages.error(request, 'El área del lote no puede superar 150 hectáreas.')
            return redirect('registros')

        codigo_labor = request.POST.get('codigo_labor', '').strip()
        labor_seleccionada = Labor.objects.filter(codigo=codigo_labor).first()
        if not labor_seleccionada:
            messages.error(request, 'Selecciona una labor válida.')
            return redirect('registros')
        cuenta_proceso = Cuenta.objects.filter(proceso=labor_seleccionada.proceso).first()
        if not cuenta_proceso:
            proceso = dict(Labor.PROCESO_CHOICES)[labor_seleccionada.proceso]
            messages.error(request, f'No hay una cuenta configurada para el proceso {proceso}.')
            return redirect('registros')

        RegistroOperativo.objects.create(
            no_boleta=request.POST.get('no_boleta', '').strip(),
            fecha_labor=request.POST.get('fecha_labor') or None,
            tipo_servicio=tipo_servicio,
            proveedor=to_title_case(request.POST.get('proveedor', '')),
            codigo_maquina=request.POST.get('codigo_maquina', '').strip() or None,
            placa=request.POST.get('placa', '').strip() or None,
            operador=to_title_case(request.POST.get('operador', '')) or None,
            finca=to_title_case(request.POST.get('finca', '')),
            lote=to_title_case(request.POST.get('lote', '')),
            area_lote=area_lote,
            actividad=to_title_case(request.POST.get('actividad', '')) or None,
            labor=labor_seleccionada.descripcion,
            corte_semilla=corte_semilla,
            finca_corte_semilla=to_title_case(finca_corte_semilla) or None,
            lote_corte_semilla=to_title_case(lote_corte_semilla) or None,
            unidades=request.POST.get('unidades') or None,
            horometro_inicial=request.POST.get('horometro_inicial') or None,
            horometro_final=request.POST.get('horometro_final') or None,
            costo_unitario=request.POST.get('costo_unitario') or None,
            num_factura=request.POST.get('num_factura', '').strip() or None,
            cuenta_contable=cuenta_proceso.codigo,
            variedad=to_title_case(request.POST.get('variedad', '')) or None if es_envio_semilla else None,
            total_paquetes=request.POST.get('total_paquetes') or None if es_envio_semilla else None,
            peso_kg=request.POST.get('peso_kg') or None if es_envio_semilla else None,
            caporal_01=to_title_case(request.POST.get('caporal_01', '')) or None,
            caporal_02=to_title_case(request.POST.get('caporal_02', '')) or None,
            mayordomo=to_title_case(request.POST.get('mayordomo', '')) or None,
            administrador=to_title_case(request.POST.get('administrador', '')) or None,
            lugar_origen=to_title_case(request.POST.get('lugar_origen', '')) or None if es_transporte else None,
            lugar_destino=to_title_case(request.POST.get('lugar_destino', '')) or None if es_transporte else None,
            observaciones=request.POST.get('observaciones', '').strip() or None,
        )
        messages.success(request, 'Boleta guardada correctamente.')
        return redirect('registros')
    
    return render(request, 'registros_operativos.html', {
        **_catalogos_registro_operativo(),
    })


@login_required
def registros_operativos_data(request):
    registros = RegistroOperativo.objects.all()
    return render(request, 'registros_operativos_data.html', {
        'registros': registros,
        'is_admin': user_is_admin(request.user),
    })

@login_required
def validar_registro_operativo(request):
    numero_boleta = request.GET.get('no_boleta', '').strip()
    registros = None

    if numero_boleta:
        registros = RegistroOperativo.objects.filter(
            no_boleta__iexact=numero_boleta
        ).order_by('-created_at')

    return render(request, 'validar_registro_operativo.html', {
        'numero_boleta': numero_boleta,
        'registros': registros,
        'is_admin': user_is_admin(request.user),
    })


@login_required
def editar_registro_operativo(request, registro_id):
    if not user_is_admin(request.user):
        messages.warning(request, 'No tienes permisos para acceder a este módulo.')
        return redirect('modulos')
    
    try:
        registro = RegistroOperativo.objects.get(id=registro_id)
    except RegistroOperativo.DoesNotExist:
        messages.error(request, 'El registro no existe.')
        return redirect('registros_data')
    
    if request.method == 'POST':
        registro.no_boleta = request.POST.get('no_boleta', '').strip() or registro.no_boleta
        registro.fecha_labor = request.POST.get('fecha_labor') or registro.fecha_labor
        registro.tipo_servicio = request.POST.get('tipo_servicio', '').strip() or registro.tipo_servicio
        es_envio_semilla = _es_servicio_envio_semilla(registro.tipo_servicio)
        es_transporte = _es_servicio_transporte(registro.tipo_servicio)
        registro.proveedor = request.POST.get('proveedor', '').strip() or registro.proveedor
        registro.codigo_maquina = request.POST.get('codigo_maquina', '').strip() or None
        registro.operador = request.POST.get('operador', '').strip() or None
        registro.finca = request.POST.get('finca', '').strip() or registro.finca
        registro.lote = request.POST.get('lote', '').strip() or registro.lote
        registro.actividad = request.POST.get('actividad', '').strip() or None
        registro.labor = request.POST.get('labor', '').strip() or None
        registro.corte_semilla = request.POST.get('corte_semilla', '').strip() or None if es_envio_semilla else None
        if es_envio_semilla and registro.corte_semilla == '1':
            registro.finca_corte_semilla = request.POST.get('finca_corte_semilla', '').strip() or None
            registro.lote_corte_semilla = request.POST.get('lote_corte_semilla', '').strip() or None
            if not registro.finca_corte_semilla or not registro.lote_corte_semilla:
                messages.error(request, 'Indica la finca y el lote donde se cortó la semilla.')
                return redirect('editar_registro', registro_id=registro.id)
        else:
            registro.finca_corte_semilla = None
            registro.lote_corte_semilla = None
        registro.unidades = request.POST.get('unidades') or None
        registro.horometro_inicial = request.POST.get('horometro_inicial') or None
        registro.horometro_final = request.POST.get('horometro_final') or None
        registro.costo_unitario = request.POST.get('costo_unitario') or None
        registro.num_factura = request.POST.get('num_factura', '').strip() or None
        registro.variedad = request.POST.get('variedad', '').strip() or None if es_envio_semilla else None
        registro.total_paquetes = request.POST.get('total_paquetes') or None if es_envio_semilla else None
        registro.peso_kg = request.POST.get('peso_kg') or None if es_envio_semilla else None
        registro.caporal_01 = request.POST.get('caporal_01', '').strip() or None
        registro.caporal_02 = request.POST.get('caporal_02', '').strip() or None
        registro.mayordomo = request.POST.get('mayordomo', '').strip() or None
        registro.administrador = request.POST.get('administrador', '').strip() or None
        registro.lugar_origen = request.POST.get('lugar_origen', '').strip() or None if es_transporte else None
        registro.lugar_destino = request.POST.get('lugar_destino', '').strip() or None if es_transporte else None
        registro.observaciones = request.POST.get('observaciones', '').strip() or None
        
        registro.save()
        messages.success(request, 'Registro actualizado correctamente.')
        return redirect('registros_data')
    
    return render(request, 'editar_registro_operativo.html', {
        'registro': registro,
        'labor_actual_catalogada': bool(
            registro.labor and Labor.objects.filter(descripcion__iexact=registro.labor).exists()
        ),
        **_catalogos_registro_operativo(),
    })


@login_required
@require_http_methods(['POST'])
def borrar_registro_operativo(request, registro_id):
    if not user_is_admin(request.user):
        messages.warning(request, 'No tienes permisos para acceder a este módulo.')
        return redirect('modulos')
    
    try:
        registro = RegistroOperativo.objects.get(id=registro_id)
        boleta_numero = registro.no_boleta
        registro.delete()
        messages.success(request, f'Registro de boleta "{boleta_numero}" eliminado correctamente.')
    except RegistroOperativo.DoesNotExist:
        messages.error(request, 'El registro no existe.')
    
    return redirect('registros_data')


@login_required
def usuarios(request):
    return render(request, 'usuarios.html', {
        'is_admin': user_is_admin(request.user)
    })


@login_required
@require_http_methods(['POST'])
def crear_usuario(request):
    if not user_is_admin(request.user):
        return JsonResponse({'success': False, 'error': 'No autorizado.'}, status=403)
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)

    codigo = payload.get('codigo', '').strip()
    email = payload.get('email', '').strip()
    password = payload.get('password', '')
    rol = payload.get('rol', '').strip()
    estado = payload.get('estado', '').strip()

    if not codigo or not email or not password or not rol:
        return JsonResponse({'success': False, 'error': 'Faltan datos requeridos.'}, status=400)

    try:
        validator = PasswordStandardValidator()
        validator.validate(password)
    except ValidationError as e:
        error_msg = e.messages[0] if hasattr(e, 'messages') and e.messages else str(e)
        return JsonResponse({'success': False, 'error': error_msg}, status=400)

    empleado = Empleado.objects.filter(puesto=codigo).first()

    if not empleado:
        return JsonResponse({'success': False, 'error': 'Empleado no encontrado.'}, status=404)

    # Validación: evitar crear un usuario si el código ya está asignado a otro usuario
    if UserProfile.objects.filter(codigo__iexact=codigo).exists():
        return JsonResponse({'success': False, 'error': 'Código ya asignado a otro usuario.'}, status=400)

    employee_names = (empleado.empleado or '').strip()
    full_name = ' '.join(filter(None, [employee_names, empleado.segundo_apellido])).strip()
    if not full_name:
        return JsonResponse({'success': False, 'error': 'El empleado no tiene nombre válido.'}, status=400)

    generator = AdminUserCreationForm()
    name_parts = [part for part in employee_names.split() if part]
    surname_parts = [part for part in (empleado.segundo_apellido or '').split() if part]
    first_surname = surname_parts[0] if surname_parts else (name_parts[-1] if len(name_parts) > 1 else employee_names)
    username = generator.generate_username(employee_names, first_surname)
    username_base = username
    contador = 1
    while User.objects.filter(username__iexact=username).exists():
        contador += 1
        username = f"{username_base}{contador}"

    first_name = name_parts[0] if name_parts else ''
    last_name = ' '.join(name_parts[1:] + ([empleado.segundo_apellido] if empleado.segundo_apellido else []))
    is_active = estado.lower() == 'activo'

    usuario = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_active=is_active,
    )

    group, _ = Group.objects.get_or_create(name=rol)
    usuario.groups.add(group)
    usuario.save()

    UserProfile.objects.create(
        usuario=usuario,
        codigo=codigo,
        puesto=empleado.nombre_puesto or empleado.puesto,
    )

    return JsonResponse({
        'success': True,
        'message': 'Usuario creado con éxito.',
        'username': username,
        'password': password,
    })


@login_required
def usuarios_creados(request):
    users = User.objects.all().order_by('-date_joined')
    usuarios_data = [
        {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'nombre': f"{user.first_name} {user.last_name}".strip() or '-',
            'grupos': ', '.join([g.name for g in user.groups.all()]) or 'Sin rol',
            'is_admin': user.groups.filter(name='Admin').exists() or user.is_superuser,
            'fecha': timezone.localtime(user.date_joined),
            'activo': 'Sí' if user.is_active else 'No',
            'is_active': user.is_active,
        }
        for user in users
    ]
    return render(request, 'usuarios_creados.html', {
        'usuarios': usuarios_data,
        'is_admin': user_is_admin(request.user)
    })


@login_required
def operacion(request):
    if not user_is_user_or_admin(request.user):
        messages.warning(request, 'No tienes permisos para acceder a este módulo.')
        return redirect('modulos')

    if request.method == 'POST':
        accion = request.POST.get('action', 'create').strip()
        tipo_servicio = request.POST.get('tipo_servicio', '').strip()
        fecha = request.POST.get('fecha') or timezone.now().date()
        finca = request.POST.get('finca', '').strip()
        lote = request.POST.get('lote', '').strip()
        area_val = request.POST.get('area', '').strip()
        responsable = request.POST.get('responsable', '').strip()
        prioridad = request.POST.get('prioridad', 'Normal').strip() or 'Normal'
        estado = request.POST.get('estado', 'Programada').strip() or 'Programada'
        observaciones = request.POST.get('observaciones', '').strip() or None

        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax') == '1'

        if not (tipo_servicio and finca and lote and area_val and responsable):
            error_msg = 'Por favor completa todos los campos requeridos (Servicio, Finca, Lote, Área y Responsable).'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('operacion')

        if accion not in ('create', 'update'):
            error_msg = 'La acción solicitada no es válida.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('operacion')

        if prioridad not in dict(ProgramacionOperacion.PRIORIDAD_CHOICES):
            prioridad = 'Normal'
        if estado not in dict(ProgramacionOperacion.ESTADO_CHOICES):
            estado = 'Programada'

        try:
            area = float(area_val)
        except (ValueError, TypeError):
            error_msg = 'La cantidad de área debe ser un número válido.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('operacion')

        if accion == 'update':
            try:
                nueva_programacion = ProgramacionOperacion.objects.get(
                    pk=request.POST.get('operacion_id')
                )
            except (ProgramacionOperacion.DoesNotExist, ValueError, TypeError):
                error_msg = 'La operación que intentas editar ya no existe.'
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error_msg}, status=404)
                messages.error(request, error_msg)
                return redirect('/operacion/?ver=logistica')

            nueva_programacion.tipo_servicio = tipo_servicio
            nueva_programacion.fecha = fecha
            nueva_programacion.finca = finca
            nueva_programacion.lote = lote
            nueva_programacion.area = area
            nueva_programacion.responsable = responsable
            nueva_programacion.prioridad = prioridad
            nueva_programacion.estado = estado
            nueva_programacion.observaciones = observaciones
            nueva_programacion.save()
            mensaje = 'Operación actualizada correctamente en Logística.'
        else:
            nueva_programacion = ProgramacionOperacion.objects.create(
                tipo_servicio=tipo_servicio,
                fecha=fecha,
                finca=finca,
                lote=lote,
                area=area,
                responsable=responsable,
                prioridad=prioridad,
                estado=estado,
                observaciones=observaciones,
                creado_por=request.user if request.user.is_authenticated else None,
            )
            mensaje = '¡Operación programada exitosamente en Logística!'

        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': mensaje,
                'id': nueva_programacion.id,
                'fecha': str(nueva_programacion.fecha),
                'tipo_servicio': nueva_programacion.tipo_servicio,
                'finca': nueva_programacion.finca,
                'lote': nueva_programacion.lote,
                'area': str(nueva_programacion.area),
                'responsable': nueva_programacion.responsable,
                'prioridad': nueva_programacion.prioridad,
                'estado': nueva_programacion.estado,
            })

        messages.success(request, mensaje)
        return redirect('/operacion/?ver=logistica')

    fincas = Auxiliar.objects.filter(tipo__icontains='finca').order_by('nombre')
    empleados = Empleado.objects.all().order_by('empleado')
    programaciones = ProgramacionOperacion.objects.all().order_by('-fecha', '-created_at')

    total_programadas = programaciones.count()
    total_area = sum((p.area for p in programaciones if p.area), 0)
    pendientes_count = programaciones.filter(estado__in=['Programada', 'En Proceso']).count()
    realizadas_count = programaciones.filter(estado='Realizada').count()

    return render(request, 'operacion.html', {
        'fincas': fincas,
        'empleados': empleados,
        'programaciones': programaciones,
        'total_programadas': total_programadas,
        'total_area': total_area,
        'pendientes_count': pendientes_count,
        'realizadas_count': realizadas_count,
        'is_admin': user_is_admin(request.user),
        'ver_logistica': request.GET.get('ver') == 'logistica',
    })


@login_required
@require_http_methods(['POST'])
def cambiar_estado_operacion(request, operacion_id):
    if not user_is_user_or_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Permiso denegado'}, status=403)
    try:
        prog = ProgramacionOperacion.objects.get(id=operacion_id)
        nuevo_estado = request.POST.get('estado', '').strip()
        if nuevo_estado in ['Programada', 'En Proceso', 'Realizada', 'Cancelada']:
            prog.estado = nuevo_estado
            prog.save()
            return JsonResponse({'success': True, 'estado': prog.estado})
        return JsonResponse({'success': False, 'error': 'Estado no válido'}, status=400)
    except ProgramacionOperacion.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Operación no encontrada'}, status=404)


@login_required
@require_http_methods(['POST'])
def eliminar_operacion_programada(request, operacion_id):
    if not user_is_user_or_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Permiso denegado'}, status=403)
    try:
        prog = ProgramacionOperacion.objects.get(id=operacion_id)
        prog.delete()
        messages.success(request, 'Operación programada eliminada correctamente.')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax') == '1':
            return JsonResponse({'success': True})
        return redirect('/operacion/?ver=logistica')
    except ProgramacionOperacion.DoesNotExist:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax') == '1':
            return JsonResponse({'success': False, 'error': 'Operación no encontrada'}, status=404)
        messages.error(request, 'La operación a eliminar no existe.')
        return redirect('/operacion/?ver=logistica')



@login_required
def reportes(request):
    tipo_reporte = request.GET.get('tipo_reporte')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    registros = None
    
    if fecha_inicio and fecha_fin:
        registros = RegistroOperativo.objects.filter(
            fecha_labor__gte=fecha_inicio,
            fecha_labor__lte=fecha_fin
        )
        if tipo_reporte:
            registros = registros.filter(tipo_servicio=tipo_reporte)
        registros = registros.order_by('-fecha_labor')
        
    return render(request, 'reportes.html', {
        'registros': registros
    })


@login_required
def indicadores(request):
    registros = RegistroOperativo.objects.all()
    totales = registros.aggregate(
        cantidad=Count('id'),
        area=Sum('area_lote'),
        total_unidades=Sum('unidades'),
        costo=Sum(ExpressionWrapper(
            F('unidades') * F('costo_unitario'),
            output_field=DecimalField(max_digits=24, decimal_places=2),
        )),
    )
    servicios = registros.values('tipo_servicio').annotate(
        cantidad=Count('id')
    ).order_by('-cantidad', 'tipo_servicio')

    return render(request, 'indicadores.html', {
        'total_registros': totales['cantidad'] or 0,
        'area_total': totales['area'] or 0,
        'unidades_totales': totales['total_unidades'] or 0,
        'costo_calculado': totales['costo'] or 0,
        'servicios': servicios,
    })


# ==================== MÓDULO: COMBUSTIBLES ====================

def _normalizar_referencia_combustible(valor):
    normalizado = unicodedata.normalize('NFKD', valor or '')
    return ''.join(
        caracter for caracter in normalizado
        if not unicodedata.combining(caracter)
    ).casefold().strip()


def _buscar_tanque_por_referencia(referencia, bloquear=False):
    tanques = TanqueCombustible.objects
    if bloquear:
        tanques = tanques.select_for_update()
    return (
        tanques.filter(codigo__iexact=referencia).first()
        or tanques.filter(nombre__iexact=referencia).first()
    )


def _siguiente_no_vale():
    anio = timezone.localdate().year
    secuencia = SecuenciaDespacho.objects.filter(pk=1).first()
    ultimo = secuencia.ultimo_numero if secuencia and secuencia.anio == anio else 0
    return f'VAL-{anio}-{ultimo + 1:04d}'


def _reservar_no_vale():
    anio = timezone.localdate().year
    secuencia = SecuenciaDespacho.objects.select_for_update().get(pk=1)
    if secuencia.anio != anio:
        secuencia.anio = anio
        secuencia.ultimo_numero = 0
    secuencia.ultimo_numero += 1
    secuencia.save(update_fields=['anio', 'ultimo_numero', 'updated_at'])
    return f'VAL-{anio}-{secuencia.ultimo_numero:04d}'


@login_required
def despacho_combustible(request):
    if not user_is_user_or_admin(request.user):
        messages.warning(request, 'No tienes permisos para acceder a este módulo.')
        return redirect('modulos')

    if request.method == 'POST':
        fecha = request.POST.get('fecha') or timezone.now().date()
        codigo_maquina = request.POST.get('codigo_maquina', '').strip()
        tipo_combustible = request.POST.get('tipo_combustible', 'Diésel').strip()
        estacion_tanque = request.POST.get('estacion_tanque', '').strip()
        galones_val = request.POST.get('galones', '').strip()
        horometro_val = request.POST.get('horometro_actual', '').strip()
        labor_codigo = request.POST.get('labor', '').strip()
        operador = request.POST.get('operador', '').strip()
        proveedor_codigo = request.POST.get('proveedor', '').strip()
        finca = request.POST.get('finca', '').strip()
        firma_codigo = request.POST.get('despachado_por', '').strip()
        observaciones = request.POST.get('observaciones', '').strip() or None
        labor = Labor.objects.filter(codigo=labor_codigo).first()
        proveedor = Proveedor.objects.filter(codigo=proveedor_codigo).first()
        firma = FirmaAutorizada.objects.filter(codigo=firma_codigo).first()

        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax') == '1'

        if not (codigo_maquina and estacion_tanque and galones_val and operador and labor and proveedor and firma):
            error_msg = 'Completa Máquina, Tanque, Labor, Galones, Operador, Proveedor y Despachado por con firma autorizada.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('despacho_combustible')

        try:
            galones = Decimal(galones_val)
            horometro = Decimal(horometro_val or '0')
            if not galones.is_finite() or not horometro.is_finite():
                raise InvalidOperation
        except (InvalidOperation, ValueError, TypeError):
            error_msg = 'Los galones y el horómetro deben ser números válidos.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('despacho_combustible')

        if galones <= 0 or horometro < 0:
            error_msg = 'Los galones deben ser mayores a cero y el horómetro no puede ser negativo.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('despacho_combustible')

        error_msg = None
        with transaction.atomic():
            tanque = _buscar_tanque_por_referencia(estacion_tanque, bloquear=True)
            if not tanque:
                error_msg = 'Selecciona un tanque válido.'
            elif tanque.estado != 'Operativo':
                error_msg = 'El tanque seleccionado no está operativo.'
            elif _normalizar_referencia_combustible(tanque.tipo_combustible) != _normalizar_referencia_combustible(tipo_combustible):
                error_msg = 'El tipo de combustible no coincide con el tanque seleccionado.'
            elif galones > Decimal(tanque.nivel_actual_galones):
                error_msg = f'Existencia insuficiente en el tanque. Disponible: {tanque.nivel_actual_galones} galones.'

            if not error_msg:
                no_vale = _reservar_no_vale()
                despacho = DespachoCombustible.objects.create(
                    no_vale=no_vale,
                    fecha=fecha,
                    codigo_maquina=codigo_maquina,
                    tipo_combustible=tipo_combustible,
                    galones=galones,
                    horometro_actual=horometro,
                    labor=labor.descripcion,
                    operador=operador,
                    estacion_tanque=tanque.codigo,
                    proveedor=proveedor.razon_social,
                    finca=finca,
                    despachado_por=firma.nombre,
                    observaciones=observaciones,
                )
                tanque.nivel_actual_galones = Decimal(tanque.nivel_actual_galones) - galones
                tanque.save(update_fields=['nivel_actual_galones', 'updated_at'])

                # Mantener actualizado el horómetro de la máquina cuando avance.
                disp = DisponibilidadMaquinaria.objects.select_for_update().filter(
                    codigo_maquina__iexact=codigo_maquina
                ).first()
                if disp and horometro > Decimal(disp.horometro_actual or 0):
                    disp.horometro_actual = horometro
                    if finca:
                        disp.finca_actual = finca
                    if operador:
                        disp.operador_asignado = operador
                    disp.save()

        if error_msg:
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('despacho_combustible')

        msg = f'¡Despacho de combustible #{no_vale} registrado con éxito ({galones} galones)!'
        if is_ajax:
            return JsonResponse({'success': True, 'message': msg, 'id': despacho.id})
        messages.success(request, msg)
        return redirect('despacho_combustible')

    despacho_edicion = None
    despacho_id = request.GET.get('editar', '').strip()
    if despacho_id:
        try:
            despacho_edicion = DespachoCombustible.objects.get(pk=despacho_id)
        except (DespachoCombustible.DoesNotExist, ValueError, TypeError):
            messages.error(request, 'El despacho que intentas editar no existe.')

    despachos = DespachoCombustible.objects.all().order_by('-fecha', '-created_at')
    maquinarias = Maquinaria.objects.all().order_by('codigo_maquina')
    empleados = Empleado.objects.all().order_by('empleado')
    labores = Labor.objects.all().order_by('proceso', 'codigo')
    tanques = TanqueCombustible.objects.all().order_by('codigo')
    proveedores = Proveedor.objects.all().order_by('razon_social')
    firmas_autorizadas = FirmaAutorizada.objects.all().order_by('nombre')
    fincas = Auxiliar.objects.filter(tipo__icontains='finca').order_by('nombre')

    total_despachos = despachos.count()
    total_galones = sum((float(d.galones) for d in despachos if d.galones), 0.0)
    promedio_despacho = (total_galones / total_despachos) if total_despachos > 0 else 0.0
    maquinas_atendidas = len(set(d.codigo_maquina for d in despachos if d.codigo_maquina))
    siguiente_vale = _siguiente_no_vale()

    return render(request, 'combustibles_despacho.html', {
        'despachos': despachos,
        'maquinarias': maquinarias,
        'empleados': empleados,
        'labores': labores,
        'tanques': tanques,
        'proveedores': proveedores,
        'firmas_autorizadas': firmas_autorizadas,
        'fincas': fincas,
        'total_despachos': total_despachos,
        'total_galones': round(total_galones, 2),
        'promedio_despacho': round(promedio_despacho, 2),
        'maquinas_atendidas': maquinas_atendidas,
        'siguiente_vale': siguiente_vale,
        'fecha_hoy': timezone.now().date(),
        'is_admin': user_is_admin(request.user),
        'despacho_edicion': despacho_edicion,
        'return_to': request.GET.get('return_to') == 'consumo',
    })


@login_required
@require_http_methods(['POST'])
def gestionar_despacho_combustible(request, despacho_id):
    if not user_is_user_or_admin(request.user):
        messages.warning(request, 'No tienes permisos para gestionar despachos.')
        return redirect('modulos')

    accion = request.POST.get('action', '').strip()
    return_to_consumo = request.POST.get('return_to') == 'consumo'
    error_msg = None
    mensaje = None

    try:
        with transaction.atomic():
            despacho = DespachoCombustible.objects.select_for_update().get(pk=despacho_id)
            tanque_anterior = _buscar_tanque_por_referencia(despacho.estacion_tanque, bloquear=True)

            if not tanque_anterior:
                error_msg = 'No se encontró el tanque asociado al despacho.'
            elif accion == 'delete':
                existencia_restaurada = Decimal(tanque_anterior.nivel_actual_galones) + Decimal(despacho.galones)
                if existencia_restaurada > Decimal(tanque_anterior.capacidad_galones):
                    error_msg = 'No se puede devolver el combustible porque se superaría la capacidad del tanque.'
                else:
                    tanque_anterior.nivel_actual_galones = existencia_restaurada
                    tanque_anterior.save(update_fields=['nivel_actual_galones', 'updated_at'])
                    despacho.delete()
                    mensaje = f'Vale {despacho.no_vale} eliminado y saldo del tanque restaurado.'
            elif accion == 'update':
                fecha = parse_date(request.POST.get('fecha', '').strip())
                codigo_maquina = request.POST.get('codigo_maquina', '').strip()
                tipo_combustible = request.POST.get('tipo_combustible', '').strip()
                labor_codigo = request.POST.get('labor', '').strip()
                operador = request.POST.get('operador', '').strip()
                tanque_codigo = request.POST.get('estacion_tanque', '').strip()
                proveedor_codigo = request.POST.get('proveedor', '').strip()
                finca = request.POST.get('finca', '').strip() or None
                firma_codigo = request.POST.get('despachado_por', '').strip()
                observaciones = request.POST.get('observaciones', '').strip() or None
                labor = Labor.objects.filter(codigo=labor_codigo).first()
                proveedor = Proveedor.objects.filter(codigo=proveedor_codigo).first()
                firma = FirmaAutorizada.objects.filter(codigo=firma_codigo).first()

                try:
                    galones = Decimal(request.POST.get('galones', '').strip())
                    horometro = Decimal(request.POST.get('horometro_actual', '').strip())
                    if not galones.is_finite() or not horometro.is_finite():
                        raise InvalidOperation
                except (InvalidOperation, ValueError, TypeError):
                    error_msg = 'Galones y horómetro deben ser números válidos.'
                    galones = Decimal('0')
                    horometro = Decimal('0')

                if not error_msg and not all((fecha, codigo_maquina, tipo_combustible, operador, tanque_codigo, labor, proveedor, firma)):
                    error_msg = 'Completa los campos requeridos del despacho y selecciona catálogos válidos.'
                elif not error_msg and (galones <= 0 or horometro < 0):
                    error_msg = 'Los galones deben ser mayores a cero y el horómetro no puede ser negativo.'

                tanque_nuevo = _buscar_tanque_por_referencia(tanque_codigo, bloquear=True) if not error_msg else None
                if not error_msg and not tanque_nuevo:
                    error_msg = 'Selecciona un tanque válido.'
                elif not error_msg and tanque_nuevo.estado != 'Operativo':
                    error_msg = 'El tanque seleccionado no está operativo.'
                elif not error_msg and _normalizar_referencia_combustible(tanque_nuevo.tipo_combustible) != _normalizar_referencia_combustible(tipo_combustible):
                    error_msg = 'El tipo de combustible no coincide con el tanque seleccionado.'

                if not error_msg and tanque_nuevo.pk == tanque_anterior.pk:
                    existencia_disponible = Decimal(tanque_nuevo.nivel_actual_galones) + Decimal(despacho.galones)
                    if existencia_disponible > Decimal(tanque_nuevo.capacidad_galones):
                        error_msg = 'No se puede restaurar el saldo porque se superaría la capacidad del tanque.'
                    elif galones > existencia_disponible:
                        error_msg = f'Existencia insuficiente en el tanque. Disponible: {existencia_disponible} galones.'
                    else:
                        tanque_nuevo.nivel_actual_galones = existencia_disponible - galones
                        tanque_nuevo.save(update_fields=['nivel_actual_galones', 'updated_at'])
                elif not error_msg:
                    existencia_anterior = Decimal(tanque_anterior.nivel_actual_galones) + Decimal(despacho.galones)
                    existencia_nueva = Decimal(tanque_nuevo.nivel_actual_galones)
                    if existencia_anterior > Decimal(tanque_anterior.capacidad_galones):
                        error_msg = 'No se puede restaurar el saldo porque se superaría la capacidad del tanque original.'
                    elif galones > existencia_nueva:
                        error_msg = f'Existencia insuficiente en el tanque seleccionado. Disponible: {existencia_nueva} galones.'
                    else:
                        tanque_anterior.nivel_actual_galones = existencia_anterior
                        tanque_nuevo.nivel_actual_galones = existencia_nueva - galones
                        tanque_anterior.save(update_fields=['nivel_actual_galones', 'updated_at'])
                        tanque_nuevo.save(update_fields=['nivel_actual_galones', 'updated_at'])

                if not error_msg:
                    despacho.fecha = fecha
                    despacho.codigo_maquina = codigo_maquina
                    despacho.tipo_combustible = tipo_combustible
                    despacho.galones = galones
                    despacho.horometro_actual = horometro
                    despacho.labor = labor.descripcion
                    despacho.operador = operador
                    despacho.estacion_tanque = tanque_nuevo.codigo
                    despacho.proveedor = proveedor.razon_social
                    despacho.finca = finca
                    despacho.despachado_por = firma.nombre
                    despacho.observaciones = observaciones
                    despacho.save()

                    disponibilidad = DisponibilidadMaquinaria.objects.select_for_update().filter(
                        codigo_maquina__iexact=codigo_maquina
                    ).first()
                    if disponibilidad and horometro > Decimal(disponibilidad.horometro_actual or 0):
                        disponibilidad.horometro_actual = horometro
                        if finca:
                            disponibilidad.finca_actual = finca
                        disponibilidad.operador_asignado = operador
                        disponibilidad.save()
                    mensaje = f'Vale {despacho.no_vale} actualizado correctamente.'
            else:
                error_msg = 'La acción solicitada no es válida.'
    except DespachoCombustible.DoesNotExist:
        error_msg = 'El despacho que intentas gestionar no existe.'

    destino = 'consumo_combustible' if return_to_consumo else 'despacho_combustible'
    if error_msg:
        messages.error(request, error_msg)
    elif mensaje:
        messages.success(request, mensaje)
    if destino == 'despacho_combustible':
        return redirect(f'{reverse(destino)}?ver=historial')
    return redirect(destino)


@login_required
def consumo_combustible(request):
    if not user_is_user_or_admin(request.user):
        messages.warning(request, 'No tienes permisos para acceder a este módulo.')
        return redirect('modulos')

    filtro_maquina = request.GET.get('maquina', '').strip()
    fecha_inicio = request.GET.get('fecha_inicio', '').strip()
    fecha_fin = request.GET.get('fecha_fin', '').strip()

    qs = DespachoCombustible.objects.all()
    if filtro_maquina:
        qs = qs.filter(codigo_maquina__iexact=filtro_maquina)
    if fecha_inicio:
        qs = qs.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        qs = qs.filter(fecha__lte=fecha_fin)

    despachos = qs.order_by('-fecha')
    total_galones = sum((float(d.galones) for d in despachos if d.galones), 0.0)
    costo_estimado = total_galones * 32.50

    por_maquina = {}
    for d in despachos:
        cod = d.codigo_maquina
        if cod not in por_maquina:
            por_maquina[cod] = {
                'codigo': cod,
                'despachos_count': 0,
                'total_galones': 0.0,
                'horometros': [],
                'tipo_combustible': d.tipo_combustible,
                'operadores': set(),
            }
        por_maquina[cod]['despachos_count'] += 1
        por_maquina[cod]['total_galones'] += float(d.galones or 0)
        if d.horometro_actual:
            por_maquina[cod]['horometros'].append(float(d.horometro_actual))
        if d.operador:
            por_maquina[cod]['operadores'].add(d.operador)

    resumen_maquinas = []
    for cod, info in por_maquina.items():
        hrs_delta = 0.0
        if len(info['horometros']) >= 2:
            hrs_delta = max(info['horometros']) - min(info['horometros'])
        rendimiento = (info['total_galones'] / hrs_delta) if hrs_delta > 0 else (info['total_galones'] / 50.0)
        pct = (info['total_galones'] / total_galones * 100) if total_galones > 0 else 0
        resumen_maquinas.append({
            'codigo': cod,
            'despachos_count': info['despachos_count'],
            'total_galones': round(info['total_galones'], 2),
            'horas_estimadas': round(hrs_delta, 1) if hrs_delta > 0 else 'N/A',
            'rendimiento': round(rendimiento, 2),
            'porcentaje': round(pct, 1),
            'costo_q': round(info['total_galones'] * 32.50, 2),
            'operadores': ', '.join(info['operadores']) or 'Varios',
        })
    resumen_maquinas.sort(key=lambda x: x['total_galones'], reverse=True)

    maquina_top = resumen_maquinas[0]['codigo'] if resumen_maquinas else 'N/A'
    rendimiento_promedio = (sum(m['rendimiento'] for m in resumen_maquinas) / len(resumen_maquinas)) if resumen_maquinas else 0.0
    maquinarias = Maquinaria.objects.all().order_by('codigo_maquina')

    return render(request, 'combustibles_consumo.html', {
        'despachos': despachos,
        'resumen_maquinas': resumen_maquinas,
        'maquinarias': maquinarias,
        'total_galones': round(total_galones, 2),
        'costo_estimado': round(costo_estimado, 2),
        'maquina_top': maquina_top,
        'rendimiento_promedio': round(rendimiento_promedio, 2),
        'filtro_maquina': filtro_maquina,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'is_admin': user_is_admin(request.user),
    })


@login_required
def tanques_combustible(request):
    if not user_is_user_or_admin(request.user):
        messages.warning(request, 'No tienes permisos para acceder a este módulo.')
        return redirect('modulos')

    if request.method == 'POST':
        action = request.POST.get('action', '').strip()
        if action in ('crear_tanque', 'editar_tanque', 'eliminar_tanque'):
            return _gestionar_tanque_combustible(request, action)

        codigo_tanque = request.POST.get('codigo_tanque', '').strip()
        if action not in ('recarga', 'ajuste'):
            messages.error(request, 'La operación solicitada no es válida.')
            return redirect('tanques_combustible')

        try:
            cantidad = Decimal(
                request.POST.get('galones_recarga' if action == 'recarga' else 'nuevo_nivel', '0') or '0'
            )
            if not cantidad.is_finite():
                raise InvalidOperation
        except (InvalidOperation, ValueError, TypeError):
            messages.error(request, 'Ingresa una cantidad numérica válida.')
            return redirect('tanques_combustible')

        with transaction.atomic():
            tanque = TanqueCombustible.objects.select_for_update().filter(
                codigo__iexact=codigo_tanque
            ).first()

            if not tanque:
                messages.error(request, 'Tanque de combustible no encontrado.')
                return redirect('tanques_combustible')

            capacidad = Decimal(tanque.capacidad_galones)
            nivel_actual = Decimal(tanque.nivel_actual_galones)

            if action == 'recarga':
                nuevo_nivel = nivel_actual + cantidad
                if cantidad <= 0:
                    messages.error(request, 'La recarga debe ser mayor a cero.')
                    return redirect('tanques_combustible')
                if nuevo_nivel > capacidad:
                    messages.error(request, 'La recarga supera la capacidad disponible del tanque.')
                    return redirect('tanques_combustible')
                tanque.nivel_actual_galones = nuevo_nivel
                tanque.save(update_fields=['nivel_actual_galones', 'updated_at'])
                messages.success(request, f'¡Recarga de {cantidad} galones aplicada a {tanque.nombre}!')
            else:
                estado = request.POST.get('estado', tanque.estado)
                if cantidad < 0 or cantidad > capacidad:
                    messages.error(request, 'El nivel debe estar entre cero y la capacidad total del tanque.')
                    return redirect('tanques_combustible')
                if estado not in dict(TanqueCombustible.ESTADO_CHOICES):
                    messages.error(request, 'El estado seleccionado no es válido.')
                    return redirect('tanques_combustible')
                tanque.nivel_actual_galones = cantidad
                tanque.estado = estado
                tanque.save(update_fields=['nivel_actual_galones', 'estado', 'updated_at'])
                messages.success(request, f'¡Nivel y estado de {tanque.nombre} actualizados correctamente!')

        return redirect('tanques_combustible')

    tanques = TanqueCombustible.objects.all().order_by('codigo')
    tanques_cards = []
    capacidad_total = 0.0
    existencia_total = 0.0

    for t in tanques:
        cap = float(t.capacidad_galones or 0)
        niv = float(t.nivel_actual_galones or 0)
        capacidad_total += cap
        existencia_total += niv
        pct = (niv / cap * 100) if cap > 0 else 0
        tanques_cards.append({
            'objeto': t,
            'capacidad': cap,
            'nivel': niv,
            'porcentaje': round(pct, 1),
            'nivel_clase': 'high' if pct >= 50 else ('medium' if pct >= 25 else 'low'),
        })

    pct_global = (existencia_total / capacidad_total * 100) if capacidad_total > 0 else 0
    tanques_operativos = tanques.filter(estado='Operativo').count()

    return render(request, 'combustibles_tanques.html', {
        'tanques_cards': tanques_cards,
        'capacidad_total': round(capacidad_total, 2),
        'existencia_total': round(existencia_total, 2),
        'pct_global': round(pct_global, 1),
        'tanques_operativos': tanques_operativos,
        'is_admin': user_is_admin(request.user),
    })


def _gestionar_tanque_combustible(request, action):
    codigo = request.POST.get('codigo', '').strip()
    codigo_original = request.POST.get('codigo_original', '').strip()
    codigo_eliminar = request.POST.get('codigo_tanque', '').strip()

    if action == 'eliminar_tanque':
        with transaction.atomic():
            tanque = TanqueCombustible.objects.select_for_update().filter(
                codigo__iexact=codigo_eliminar
            ).first()
            if not tanque:
                messages.error(request, 'Tanque de combustible no encontrado.')
            else:
                tiene_historial = DespachoCombustible.objects.filter(
                    Q(estacion_tanque__iexact=tanque.nombre)
                    | Q(estacion_tanque__iexact=tanque.codigo)
                ).exists()
                if tiene_historial:
                    messages.error(request, 'No se puede eliminar un tanque con despachos registrados.')
                else:
                    nombre = tanque.nombre
                    tanque.delete()
                    messages.success(request, f'Tanque {nombre} eliminado correctamente.')
        return redirect('tanques_combustible')

    nombre = request.POST.get('nombre', '').strip()
    tipo_combustible = request.POST.get('tipo_combustible', '').strip()
    ubicacion = request.POST.get('ubicacion', '').strip()
    estado = request.POST.get('estado', 'Operativo').strip()
    try:
        capacidad = Decimal(request.POST.get('capacidad_galones', '').strip())
        nivel_actual = Decimal(request.POST.get('nivel_actual_galones', '').strip())
        if not capacidad.is_finite() or not nivel_actual.is_finite():
            raise InvalidOperation
    except (InvalidOperation, ValueError, TypeError):
        messages.error(request, 'La capacidad y el nivel deben ser números válidos.')
        return redirect('tanques_combustible')

    if not all((codigo, nombre, tipo_combustible, ubicacion)):
        messages.error(request, 'Completa todos los campos requeridos del tanque.')
        return redirect('tanques_combustible')
    if capacidad <= 0 or nivel_actual < 0 or nivel_actual > capacidad:
        messages.error(request, 'El nivel debe estar entre cero y la capacidad del tanque, que debe ser mayor a cero.')
        return redirect('tanques_combustible')
    if estado not in dict(TanqueCombustible.ESTADO_CHOICES):
        messages.error(request, 'El estado seleccionado no es válido.')
        return redirect('tanques_combustible')
    if action == 'editar_tanque' and not codigo_original:
        messages.error(request, 'No se identificó el tanque que deseas editar.')
        return redirect('tanques_combustible')

    with transaction.atomic():
        tanque = None
        if action == 'editar_tanque':
            tanque = TanqueCombustible.objects.select_for_update().filter(
                codigo__iexact=codigo_original
            ).first()
            if not tanque:
                messages.error(request, 'Tanque de combustible no encontrado.')
                return redirect('tanques_combustible')

        duplicado = TanqueCombustible.objects.filter(codigo__iexact=codigo)
        if tanque:
            duplicado = duplicado.exclude(pk=tanque.pk)
        if duplicado.exists():
            messages.error(request, f'Ya existe un tanque con el código "{codigo}".')
            return redirect('tanques_combustible')

        if action == 'crear_tanque':
            TanqueCombustible.objects.create(
                codigo=codigo,
                nombre=nombre,
                tipo_combustible=tipo_combustible,
                capacidad_galones=capacidad,
                nivel_actual_galones=nivel_actual,
                ubicacion=ubicacion,
                estado=estado,
            )
            messages.success(request, f'Tanque {nombre} creado correctamente.')
        else:
            referencias_anteriores = (tanque.nombre, tanque.codigo)
            tanque.codigo = codigo
            tanque.nombre = nombre
            tanque.tipo_combustible = tipo_combustible
            tanque.capacidad_galones = capacidad
            tanque.nivel_actual_galones = nivel_actual
            tanque.ubicacion = ubicacion
            tanque.estado = estado
            tanque.save()
            DespachoCombustible.objects.filter(
                Q(estacion_tanque__iexact=referencias_anteriores[0])
                | Q(estacion_tanque__iexact=referencias_anteriores[1])
            ).update(estacion_tanque=nombre)
            messages.success(request, f'Tanque {nombre} actualizado correctamente.')

    return redirect('tanques_combustible')


# ==================== MÓDULO: MAQUINARIA Y MANTENIMIENTO ====================

@login_required
def ordenes_mantenimiento(request):
    if not user_is_user_or_admin(request.user):
        messages.warning(request, 'No tienes permisos para acceder a este módulo.')
        return redirect('modulos')

    if request.method == 'POST':
        codigo_orden = request.POST.get('codigo_orden', '').strip()
        fecha_ingreso = request.POST.get('fecha_ingreso') or timezone.now().date()
        codigo_maquina = request.POST.get('codigo_maquina', '').strip()
        tipo_mantenimiento = request.POST.get('tipo_mantenimiento', 'Preventivo').strip()
        prioridad = request.POST.get('prioridad', 'Media').strip()
        mecanico = request.POST.get('mecanico', '').strip()
        horometro_val = request.POST.get('horometro', '0').strip()
        falla_reportada = request.POST.get('falla_reportada', '').strip()
        costo_val = request.POST.get('costo_estimado', '0').strip()
        fecha_entrega = request.POST.get('fecha_entrega') or None

        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax') == '1'

        if not (codigo_orden and codigo_maquina and mecanico and falla_reportada):
            error_msg = 'Por favor completa los campos requeridos: Código Orden, Máquina, Mecánico y Descripción de Falla.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('ordenes_mantenimiento')

        try:
            horometro = float(horometro_val or 0)
            costo = float(costo_val or 0)
        except (ValueError, TypeError):
            error_msg = 'Horómetro y costo deben ser números válidos.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('ordenes_mantenimiento')

        if OrdenMantenimiento.objects.filter(codigo_orden__iexact=codigo_orden).exists():
            error_msg = f'Ya existe una orden con el código "{codigo_orden}".'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('ordenes_mantenimiento')

        nueva_orden = OrdenMantenimiento.objects.create(
            codigo_orden=codigo_orden,
            fecha_ingreso=fecha_ingreso,
            codigo_maquina=codigo_maquina,
            tipo_mantenimiento=tipo_mantenimiento,
            prioridad=prioridad,
            estado='Pendiente',
            mecanico=mecanico,
            horometro=horometro,
            falla_reportada=falla_reportada,
            costo_estimado=costo,
            fecha_entrega=fecha_entrega,
        )

        msg = f'¡Orden de mantenimiento {codigo_orden} creada correctamente para {codigo_maquina}!'
        if is_ajax:
            return JsonResponse({'success': True, 'message': msg, 'id': nueva_orden.id})
        messages.success(request, msg)
        return redirect('ordenes_mantenimiento')

    filtro_estado = request.GET.get('estado', '').strip()
    filtro_tipo = request.GET.get('tipo', '').strip()

    qs = OrdenMantenimiento.objects.all().order_by('-fecha_ingreso', '-created_at')
    if filtro_estado:
        qs = qs.filter(estado__iexact=filtro_estado)
    if filtro_tipo:
        qs = qs.filter(tipo_mantenimiento__iexact=filtro_tipo)

    ordenes = qs
    todas_ordenes = OrdenMantenimiento.objects.all()

    total_ordenes = todas_ordenes.count()
    en_taller = todas_ordenes.filter(estado='En Taller').count()
    pendientes = todas_ordenes.filter(estado='Pendiente').count()
    finalizadas = todas_ordenes.filter(estado='Finalizada').count()
    costo_total = sum((float(o.costo_estimado or 0) for o in todas_ordenes), 0.0)

    siguiente_codigo = f"OT-{timezone.now().year}-{total_ordenes + 1:03d}"
    maquinarias = Maquinaria.objects.all().order_by('codigo_maquina')
    mecanicos = Empleado.objects.filter(puesto__in=['3300', '3400', '4310']).order_by('empleado')
    if not mecanicos.exists():
        mecanicos = Empleado.objects.all().order_by('empleado')

    return render(request, 'mantenimiento_ordenes.html', {
        'ordenes': ordenes,
        'maquinarias': maquinarias,
        'mecanicos': mecanicos,
        'total_ordenes': total_ordenes,
        'en_taller': en_taller,
        'pendientes': pendientes,
        'finalizadas': finalizadas,
        'costo_total': round(costo_total, 2),
        'siguiente_codigo': siguiente_codigo,
        'fecha_hoy': timezone.now().date(),
        'filtro_estado': filtro_estado,
        'filtro_tipo': filtro_tipo,
        'is_admin': user_is_admin(request.user),
    })


@login_required
@require_http_methods(['POST'])
def cambiar_estado_orden_mantenimiento(request, orden_id):
    if not user_is_user_or_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Permiso denegado'}, status=403)
    try:
        orden = OrdenMantenimiento.objects.get(id=orden_id)
        nuevo_estado = request.POST.get('estado', '').strip()
        trabajos = request.POST.get('trabajos_realizados', '').strip()
        costo = request.POST.get('costo_estimado', '').strip()

        if nuevo_estado in ['Pendiente', 'En Taller', 'Finalizada', 'Cancelada']:
            orden.estado = nuevo_estado
            if trabajos:
                orden.trabajos_realizados = trabajos
            if costo:
                try:
                    orden.costo_estimado = float(costo)
                except ValueError:
                    pass
            if nuevo_estado == 'Finalizada' and not orden.fecha_entrega:
                orden.fecha_entrega = timezone.now().date()
            orden.save()

            disp = DisponibilidadMaquinaria.objects.filter(codigo_maquina__iexact=orden.codigo_maquina).first()
            if disp:
                if nuevo_estado == 'En Taller':
                    disp.estado = 'En Taller'
                    disp.save()
                elif nuevo_estado == 'Finalizada':
                    disp.estado = 'Disponible'
                    disp.save()

            messages.success(request, f'Orden {orden.codigo_orden} actualizada a "{nuevo_estado}".')
            return JsonResponse({'success': True, 'estado': orden.estado})
        return JsonResponse({'success': False, 'error': 'Estado no válido'}, status=400)
    except OrdenMantenimiento.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Orden no encontrada'}, status=404)


@login_required
def control_horometros(request):
    if not user_is_user_or_admin(request.user):
        messages.warning(request, 'No tienes permisos para acceder a este módulo.')
        return redirect('modulos')

    if request.method == 'POST':
        codigo_maquina = request.POST.get('codigo_maquina', '').strip()
        tipo_servicio = request.POST.get('tipo_servicio', '').strip()
        horometro_ejecutado = float(request.POST.get('horometro_ejecutado', 0) or 0)
        intervalo = int(request.POST.get('intervalo_horas', 250) or 250)
        observaciones = request.POST.get('observaciones', '').strip()

        servicio = ControlServicioHorometro.objects.filter(
            codigo_maquina__iexact=codigo_maquina,
            tipo_servicio__iexact=tipo_servicio
        ).first()

        proximo = horometro_ejecutado + intervalo

        if servicio:
            servicio.ultimo_horometro = horometro_ejecutado
            servicio.proximo_horometro = proximo
            servicio.horometro_actual = horometro_ejecutado
            servicio.estado_alerta = 'Al Día'
            servicio.fecha_ultimo_servicio = timezone.now().date()
            if observaciones:
                servicio.observaciones = observaciones
            servicio.save()
        else:
            ControlServicioHorometro.objects.create(
                codigo_maquina=codigo_maquina,
                tipo_servicio=tipo_servicio,
                intervalo_horas=intervalo,
                ultimo_horometro=horometro_ejecutado,
                proximo_horometro=proximo,
                horometro_actual=horometro_ejecutado,
                estado_alerta='Al Día',
                fecha_ultimo_servicio=timezone.now().date(),
                observaciones=observaciones or 'Servicio preventivo registrado.'
            )

        messages.success(request, f'¡Servicio preventivo registrado para {codigo_maquina}! Próximo servicio a las {proximo}h.')
        return redirect('control_horometros')

    controles = ControlServicioHorometro.objects.all().order_by('codigo_maquina')
    maquinarias = Maquinaria.objects.all().order_by('codigo_maquina')

    items = []
    total_al_dia = 0
    total_proximos = 0
    total_vencidos = 0

    for c in controles:
        actual = float(c.horometro_actual or 0)
        proximo = float(c.proximo_horometro or 0)
        ultimo = float(c.ultimo_horometro or 0)
        restante = proximo - actual

        if restante <= 0:
            alerta = 'Vencido'
            total_vencidos += 1
        elif restante <= 25:
            alerta = 'Próximo a Vencer'
            total_proximos += 1
        else:
            alerta = 'Al Día'
            total_al_dia += 1

        if c.estado_alerta != alerta:
            c.estado_alerta = alerta
            c.save()

        intervalo = float(c.intervalo_horas or 250)
        recorrido = actual - ultimo
        pct_uso = min(100.0, max(0.0, (recorrido / intervalo * 100))) if intervalo > 0 else 0.0

        items.append({
            'control': c,
            'restante': round(restante, 1),
            'pct_uso': round(pct_uso, 1),
            'alerta': alerta,
        })

    return render(request, 'mantenimiento_horometros.html', {
        'items': items,
        'maquinarias': maquinarias,
        'total_monitoreadas': len(items),
        'total_al_dia': total_al_dia,
        'total_proximos': total_proximos,
        'total_vencidos': total_vencidos,
        'is_admin': user_is_admin(request.user),
    })


@login_required
def estado_maquinaria(request):
    if not user_is_user_or_admin(request.user):
        messages.warning(request, 'No tienes permisos para acceder a este módulo.')
        return redirect('modulos')

    if request.method == 'POST':
        codigo_maquina = request.POST.get('codigo_maquina', '').strip()
        nuevo_estado = request.POST.get('estado', '').strip()
        finca = request.POST.get('finca_actual', '').strip()
        operador = request.POST.get('operador_asignado', '').strip()
        observaciones = request.POST.get('observaciones', '').strip()

        disp, _ = DisponibilidadMaquinaria.objects.get_or_create(codigo_maquina=codigo_maquina)
        if nuevo_estado in ['Disponible', 'En Campo', 'En Taller', 'Fuera de Servicio']:
            disp.estado = nuevo_estado
        if finca:
            disp.finca_actual = finca
        if operador:
            disp.operador_asignado = operador
        if observaciones:
            disp.observaciones = observaciones
        disp.save()

        messages.success(request, f'Estado de {codigo_maquina} actualizado a "{disp.estado}".')
        return redirect('estado_maquinaria')

    filtro_estado = request.GET.get('estado', '').strip()
    filtro_tipo_maquina = request.GET.get('tipo_maquina', '').strip()
    busqueda = request.GET.get('q', '').strip()

    maquinarias = Maquinaria.objects.all().order_by('codigo_maquina')
    tipos_maquina = Maquinaria.objects.exclude(tipo_maquina='').values_list(
        'tipo_maquina', flat=True
    ).distinct().order_by('tipo_maquina')
    disponibilidades = {d.codigo_maquina: d for d in DisponibilidadMaquinaria.objects.all()}

    flota = []
    conteo_estados = {
        'total': maquinarias.count(),
        'disponible': 0,
        'en_campo': 0,
        'en_taller': 0,
        'fuera_de_servicio': 0,
    }

    for m in maquinarias:
        disp = disponibilidades.get(m.codigo_maquina)
        estado = disp.estado if disp else 'Disponible'
        finca = disp.finca_actual if disp else 'Patio Central'
        operador = disp.operador_asignado if disp else 'Sin asignar'
        horometro = disp.horometro_actual if disp else 0.0

        clave_estado = estado.lower().replace(' ', '_')
        conteo_estados[clave_estado] = conteo_estados.get(clave_estado, 0) + 1

        if filtro_estado and estado.lower() != filtro_estado.lower():
            continue

        if filtro_tipo_maquina and (m.tipo_maquina or '').casefold() != filtro_tipo_maquina.casefold():
            continue

        if busqueda:
            q_lower = busqueda.lower()
            encontrado = (
                q_lower in m.codigo_maquina.lower() or
                q_lower in (m.tipo_maquina or '').lower() or
                q_lower in (m.marca_maquina or '').lower() or
                q_lower in (m.placa_matricula or '').lower()
            )
            if not encontrado:
                continue

        flota.append({
            'maquina': m,
            'estado': estado,
            'finca': finca,
            'operador': operador,
            'horometro': horometro,
        })

    fincas = Auxiliar.objects.filter(tipo__icontains='finca').order_by('nombre')
    empleados = Empleado.objects.all().order_by('empleado')

    return render(request, 'mantenimiento_flota.html', {
        'flota': flota,
        'fincas': fincas,
        'empleados': empleados,
        'conteo_estados': conteo_estados,
        'filtro_estado': filtro_estado,
        'tipos_maquina': tipos_maquina,
        'filtro_tipo_maquina': filtro_tipo_maquina,
        'busqueda': busqueda,
        'is_admin': user_is_admin(request.user),
    })
