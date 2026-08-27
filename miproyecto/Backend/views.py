import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_http_methods

# Vistas principales del sistema agrícola y de administración.
# Aquí se gestionan las páginas de acceso, módulos, registros operativos,
# edición y eliminación, así como el control de permisos para cada usuario.

from django.core.exceptions import ValidationError
from accounts.forms import AdminUserCreationForm
from accounts.validators import PasswordStandardValidator
from accounts.models import Empleado, UserProfile, RegistroOperativo, Proveedor, Maquinaria, Auxiliar, Labor, Variedad, Municipio


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
    """
    Convierte una cadena a formato Nombre Propio / Letra Inicial Mayúscula en cada palabra.
    Preserva valores nulos, vacíos o numéricos.
    """
    if not val or not isinstance(val, str):
        return val
    val = val.strip()
    if not val:
        return val
    words = []
    for word in val.split():
        if word.isupper() and len(word) <= 4:
            words.append(word)
        else:
            words.append(word[:1].upper() + word[1:].lower())
    return ' '.join(words)


@login_required
def registros_operativos(request):
    if not user_is_user_or_admin(request.user):
        messages.warning(request, 'No tienes permisos para acceder a este módulo.')
        return redirect('modulos')
    if request.method == 'POST':
        RegistroOperativo.objects.create(
            no_boleta=request.POST.get('no_boleta', '').strip(),
            fecha_labor=request.POST.get('fecha_labor') or None,
            tipo_servicio=to_title_case(request.POST.get('tipo_servicio', '')),
            proveedor=to_title_case(request.POST.get('proveedor', '')),
            codigo_maquina=request.POST.get('codigo_maquina', '').strip() or None,
            placa=request.POST.get('placa', '').strip() or None,
            operador=to_title_case(request.POST.get('operador', '')) or None,
            finca=to_title_case(request.POST.get('finca', '')),
            lote=to_title_case(request.POST.get('lote', '')),
            area_lote=request.POST.get('area_lote') or None,
            actividad=to_title_case(request.POST.get('actividad', '')) or None,
            labor=to_title_case(request.POST.get('labor', '')) or None,
            corte_semilla=request.POST.get('corte_semilla', '').strip() or None,
            unidades=request.POST.get('unidades') or None,
            horometro_inicial=request.POST.get('horometro_inicial') or None,
            horometro_final=request.POST.get('horometro_final') or None,
            costo_unitario=request.POST.get('costo_unitario') or None,
            num_factura=request.POST.get('num_factura', '').strip() or None,
            cuenta_contable=request.POST.get('cuenta_contable', '').strip() or None,
            variedad=to_title_case(request.POST.get('variedad', '')) or None,
            total_paquetes=request.POST.get('total_paquetes') or None,
            peso_kg=request.POST.get('peso_kg') or None,
            caporal_01=to_title_case(request.POST.get('caporal_01', '')) or None,
            caporal_02=to_title_case(request.POST.get('caporal_02', '')) or None,
            mayordomo=to_title_case(request.POST.get('mayordomo', '')) or None,
            administrador=to_title_case(request.POST.get('administrador', '')) or None,
            lugar_origen=to_title_case(request.POST.get('lugar_origen', '')) or None,
            lugar_destino=to_title_case(request.POST.get('lugar_destino', '')) or None,
            observaciones=request.POST.get('observaciones', '').strip() or None,
        )
        messages.success(request, 'Boleta guardada correctamente.')
        return redirect('registros')
    
    proveedores = Proveedor.objects.all().order_by('razon_social')
    maquinarias = Maquinaria.objects.all().order_by('codigo_maquina')
    fincas = Auxiliar.objects.filter(tipo__icontains='finca').order_by('nombre')
    labores = Labor.objects.all().order_by('codigo')
    variedades = Variedad.objects.all().order_by('descripcion')
    municipios = Municipio.objects.all().order_by('nombre')
    
    return render(request, 'registros_operativos.html', {
        'proveedores': proveedores,
        'maquinarias': maquinarias,
        'fincas': fincas,
        'labores': labores,
        'variedades': variedades,
        'municipios': municipios,
    })


@login_required
def registros_operativos_data(request):
    registros = RegistroOperativo.objects.all()
    return render(request, 'registros_operativos_data.html', {
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
        registro.proveedor = request.POST.get('proveedor', '').strip() or registro.proveedor
        registro.codigo_maquina = request.POST.get('codigo_maquina', '').strip() or None
        registro.placa = request.POST.get('placa', '').strip() or None
        registro.operador = request.POST.get('operador', '').strip() or None
        registro.finca = request.POST.get('finca', '').strip() or registro.finca
        registro.lote = request.POST.get('lote', '').strip() or registro.lote
        registro.area_lote = request.POST.get('area_lote') or None
        registro.actividad = request.POST.get('actividad', '').strip() or None
        registro.labor = request.POST.get('labor', '').strip() or None
        registro.corte_semilla = request.POST.get('corte_semilla', '').strip() or None
        registro.unidades = request.POST.get('unidades') or None
        registro.horometro_inicial = request.POST.get('horometro_inicial') or None
        registro.horometro_final = request.POST.get('horometro_final') or None
        registro.costo_unitario = request.POST.get('costo_unitario') or None
        registro.num_factura = request.POST.get('num_factura', '').strip() or None
        registro.cuenta_contable = request.POST.get('cuenta_contable', '').strip() or None
        registro.variedad = request.POST.get('variedad', '').strip() or None
        registro.total_paquetes = request.POST.get('total_paquetes') or None
        registro.peso_kg = request.POST.get('peso_kg') or None
        registro.caporal_01 = request.POST.get('caporal_01', '').strip() or None
        registro.caporal_02 = request.POST.get('caporal_02', '').strip() or None
        registro.mayordomo = request.POST.get('mayordomo', '').strip() or None
        registro.administrador = request.POST.get('administrador', '').strip() or None
        registro.lugar_origen = request.POST.get('lugar_origen', '').strip() or None
        registro.lugar_destino = request.POST.get('lugar_destino', '').strip() or None
        registro.observaciones = request.POST.get('observaciones', '').strip() or None
        
        registro.save()
        messages.success(request, 'Registro actualizado correctamente.')
        return redirect('registros_data')
    
    proveedores = Proveedor.objects.all().order_by('razon_social')
    maquinarias = Maquinaria.objects.all().order_by('codigo_maquina')
    fincas = Auxiliar.objects.filter(tipo__icontains='finca').order_by('nombre')
    labores = Labor.objects.all().order_by('codigo')
    variedades = Variedad.objects.all().order_by('descripcion')
    municipios = Municipio.objects.all().order_by('nombre')
    
    return render(request, 'editar_registro_operativo.html', {
        'registro': registro,
        'proveedores': proveedores,
        'maquinarias': maquinarias,
        'fincas': fincas,
        'labores': labores,
        'variedades': variedades,
        'municipios': municipios,
    })


@login_required
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
    return render(request, 'operacion.html')


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
