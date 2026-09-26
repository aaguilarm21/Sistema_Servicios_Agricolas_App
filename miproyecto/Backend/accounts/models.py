from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator, RegexValidator


SIGLAS = {
    'api': 'API',
    'cui': 'CUI',
    'dpi': 'DPI',
    'gps': 'GPS',
    'it': 'IT',
    'iva': 'IVA',
    'nit': 'NIT',
    'rtk': 'RTK',
    's/n': 'S/N',
    'sat': 'SAT',
}

CAMPOS_IDENTIFICACION = frozenset({
    'codigo',
    'codigo_articulo',
    'codigo_maquina',
    'cuenta_contable',
    'id_proveedor',
    'nit',
    'no_boleta',
    'no_cui',
    'num_factura',
    'placa',
    'placa_matricula',
    'serie_maquina',
})


def normalizar_texto(valor):
    if not isinstance(valor, str) or not valor.strip() or valor.strip().isdigit():
        return valor
    return ' '.join(
        SIGLAS.get(palabra.casefold(), palabra[:1].upper() + palabra[1:].lower())
        for palabra in valor.strip().split()
    )


class ModeloTextoNormalizado(models.Model):
    CAMPOS_IDENTIFICACION = frozenset()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        campos_identificacion = CAMPOS_IDENTIFICACION | self.CAMPOS_IDENTIFICACION
        for campo in self._meta.concrete_fields:
            if isinstance(campo, (models.CharField, models.TextField)) and campo.name not in campos_identificacion:
                valor = getattr(self, campo.attname)
                setattr(self, campo.attname, normalizar_texto(valor))
        super().save(*args, **kwargs)


class UserProfile(ModeloTextoNormalizado):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Código')
    puesto = models.CharField(max_length=150, verbose_name='Puesto')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'

    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.codigo}"


class Proveedor(ModeloTextoNormalizado):
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Código')
    nit = models.CharField(max_length=20, verbose_name='NIT')
    razon_social = models.CharField(max_length=200, verbose_name='Razón Social')
    nombre_propietario = models.CharField(max_length=150, verbose_name='Nombre Propietario')
    regimen_tributario = models.CharField(max_length=100, verbose_name='Régimen Tributario')
    tipo_factura = models.CharField(max_length=100, verbose_name='Tipo Factura')
    dias_credito = models.IntegerField(verbose_name='Días Crédito', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.codigo} - {self.razon_social}"


class Empleado(ModeloTextoNormalizado):
    CAMPOS_IDENTIFICACION = frozenset({'puesto'})

    empresa = models.CharField(max_length=200, verbose_name='Empresa')
    empleado = models.CharField(max_length=150, verbose_name='Empleado')
    segundo_apellido = models.CharField(max_length=100, verbose_name='Segundo Apellido')
    no_cui = models.CharField(
        max_length=13,
        verbose_name='No. CUI',
        validators=[
            MaxLengthValidator(13),
            RegexValidator(r'^\d{1,13}$', 'El No. CUI debe contener únicamente dígitos y no superar 13 caracteres.'),
        ],
    )
    puesto = models.CharField(max_length=100, verbose_name='Puesto')
    nombre_puesto = models.CharField(max_length=150, verbose_name='Nombre Puesto')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.empleado} - {self.nombre_puesto}"


class Maquinaria(ModeloTextoNormalizado):
    codigo_maquina = models.CharField(max_length=50, unique=True, verbose_name='Código Máquina')
    combustible = models.CharField(max_length=10, verbose_name='Combustible S/N')
    id_proveedor = models.CharField(max_length=50, verbose_name='ID Proveedor', blank=True, null=True)
    tipo_maquina = models.CharField(max_length=150, verbose_name='Tipo Máquina')
    marca_maquina = models.CharField(max_length=150, verbose_name='Marca Máquina')
    serie_maquina = models.CharField(max_length=150, verbose_name='Serie Máquina')
    placa_matricula = models.CharField(max_length=50, verbose_name='Placa o Matrícula')
    observaciones = models.TextField(verbose_name='Observaciones', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Maquinaria'
        verbose_name_plural = 'Maquinaria'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.codigo_maquina} - {self.tipo_maquina}"


class Bodega(ModeloTextoNormalizado):
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Código')
    nombre_bodega = models.CharField(max_length=200, verbose_name='Nombre Bodega')
    unidad_medida = models.CharField(max_length=50, verbose_name='Unidad Medida')
    capacidad = models.CharField(max_length=50, verbose_name='Capacidad')
    observaciones = models.TextField(verbose_name='Observaciones', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Bodega'
        verbose_name_plural = 'Bodegas'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.codigo} - {self.nombre_bodega}"


class Articulo(ModeloTextoNormalizado):
    codigo_articulo = models.CharField(max_length=50, unique=True, verbose_name='Código artículo')
    descripcion = models.CharField(max_length=250, verbose_name='Descripción')
    unidad_medida = models.CharField(max_length=50, verbose_name='Unidad de Medida')
    categoria = models.CharField(max_length=100, verbose_name='Categoría')
    stock = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Stock', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Artículo'
        verbose_name_plural = 'Artículos'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.codigo_articulo} - {self.descripcion}"



# ==================== CATALOGOS AUXILIARES ====================

class Labor(ModeloTextoNormalizado):
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Codigo')
    descripcion = models.CharField(max_length=200, verbose_name='Descripcion')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Labor'
        verbose_name_plural = 'Labores'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


class Cuenta(ModeloTextoNormalizado):
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Codigo')
    descripcion = models.CharField(max_length=200, verbose_name='Descripcion')
    tipo = models.CharField(max_length=100, verbose_name='Tipo', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


class UnidadMedida(ModeloTextoNormalizado):
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Codigo')
    descripcion = models.CharField(max_length=150, verbose_name='Descripcion')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


class NombrePuesto(ModeloTextoNormalizado):
    nombre = models.CharField(max_length=150, unique=True, verbose_name='Nombre Puesto')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Nombre de Puesto'
        verbose_name_plural = 'Nombres de Puesto'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Variedad(ModeloTextoNormalizado):
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Codigo')
    descripcion = models.CharField(max_length=200, verbose_name='Descripcion')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Variedad'
        verbose_name_plural = 'Variedades'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


class TipoMaquina(ModeloTextoNormalizado):
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Codigo')
    descripcion = models.CharField(max_length=200, verbose_name='Descripcion')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tipo de Maquina'
        verbose_name_plural = 'Tipos de Maquina'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


class Marca(ModeloTextoNormalizado):
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Codigo')
    descripcion = models.CharField(max_length=200, verbose_name='Descripcion')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


class Municipio(ModeloTextoNormalizado):
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Codigo')
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    departamento = models.CharField(max_length=150, verbose_name='Departamento', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Municipio'
        verbose_name_plural = 'Municipios'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class Auxiliar(ModeloTextoNormalizado):
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Codigo')
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    tipo = models.CharField(max_length=100, verbose_name='Tipo', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Auxiliar'
        verbose_name_plural = 'Auxiliares'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class RegistroOperativo(ModeloTextoNormalizado):
    no_boleta = models.CharField(max_length=100, verbose_name='No. Boleta')
    fecha_labor = models.DateField(verbose_name='Fecha Labor')
    tipo_servicio = models.CharField(max_length=100, verbose_name='Tipo Servicio')
    proveedor = models.CharField(max_length=200, verbose_name='Proveedor')
    codigo_maquina = models.CharField(max_length=100, verbose_name='Código Máquina', blank=True, null=True)
    placa = models.CharField(max_length=100, verbose_name='Placa', blank=True, null=True)
    operador = models.CharField(max_length=200, verbose_name='Operador', blank=True, null=True)
    finca = models.CharField(max_length=200, verbose_name='Finca')
    lote = models.CharField(max_length=200, verbose_name='Caña / Lote')
    area_lote = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Área Lote (Ha)', blank=True, null=True)
    actividad = models.CharField(max_length=200, verbose_name='Actividad', blank=True, null=True)
    labor = models.CharField(max_length=200, verbose_name='Labor', blank=True, null=True)
    corte_semilla = models.CharField(max_length=20, verbose_name='Lote Corte Semilla', blank=True, null=True)
    unidades = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Unidades', blank=True, null=True)
    horometro_inicial = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Horómetro Inicial', blank=True, null=True)
    horometro_final = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Horómetro Final', blank=True, null=True)
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Costo Unitario', blank=True, null=True)
    num_factura = models.CharField(max_length=100, verbose_name='No. Factura', blank=True, null=True)
    cuenta_contable = models.CharField(max_length=150, verbose_name='Cuenta Contable', blank=True, null=True)
    variedad = models.CharField(max_length=150, verbose_name='Variedad', blank=True, null=True)
    total_paquetes = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Total Paq/Cajas', blank=True, null=True)
    peso_kg = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Peso Kg', blank=True, null=True)
    caporal_01 = models.CharField(max_length=150, verbose_name='Caporal 01', blank=True, null=True)
    caporal_02 = models.CharField(max_length=150, verbose_name='Caporal 02', blank=True, null=True)
    mayordomo = models.CharField(max_length=150, verbose_name='Mayordomo', blank=True, null=True)
    administrador = models.CharField(max_length=150, verbose_name='Administrador', blank=True, null=True)
    lugar_origen = models.CharField(max_length=200, verbose_name='Lugar de Origen', blank=True, null=True)
    lugar_destino = models.CharField(max_length=200, verbose_name='Lugar de Destino', blank=True, null=True)
    observaciones = models.TextField(verbose_name='Observaciones', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Registro Operativo'
        verbose_name_plural = 'Registros Operativos'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.no_boleta} - {self.fecha_labor}"


class ProgramacionOperacion(ModeloTextoNormalizado):
    ESTADO_CHOICES = [
        ('Programada', 'Programada'),
        ('En Proceso', 'En Proceso'),
        ('Realizada', 'Realizada'),
        ('Cancelada', 'Cancelada'),
    ]

    PRIORIDAD_CHOICES = [
        ('Baja', 'Baja'),
        ('Normal', 'Normal'),
        ('Alta', 'Alta'),
        ('Urgente', 'Urgente'),
    ]

    tipo_servicio = models.CharField(max_length=150, verbose_name='Tipo de Servicio')
    fecha = models.DateField(verbose_name='Fecha Programada')
    finca = models.CharField(max_length=200, verbose_name='Finca')
    lote = models.CharField(max_length=100, verbose_name='Lote')
    area = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Cantidad de Área (Ha)')
    responsable = models.CharField(max_length=200, verbose_name='Responsable de la Operación')
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='Normal', verbose_name='Prioridad')
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='Programada', verbose_name='Estado')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Descripción / Observaciones')
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Creado por')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Modificación')

    class Meta:
        verbose_name = 'Programación de Operación'
        verbose_name_plural = 'Programaciones de Operaciones'
        ordering = ['-fecha', '-created_at']

    def __str__(self):
        return f"{self.tipo_servicio} - {self.finca} ({self.lote}) [{self.fecha}]"


class FirmaAutorizada(ModeloTextoNormalizado):
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    puesto = models.CharField(max_length=150, verbose_name='Puesto')
    area = models.CharField(max_length=150, verbose_name='Área')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Firma Autorizada'
        verbose_name_plural = 'Firmas Autorizadas'
        ordering = ['area', 'nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class LoginAttempt(models.Model):
    DEVICE_CHOICES = [
        ('mobile', 'Móvil'),
        ('tablet', 'Tableta'),
        ('pc', 'PC'),
        ('unknown', 'Desconocido'),
    ]

    LOCATION_STATUS_CHOICES = [
        ('captured', 'GPS capturado'),
        ('not_shared', 'No compartida'),
        ('denied', 'Permiso denegado'),
        ('unavailable', 'No disponible'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='login_attempts',
        blank=True,
        null=True,
    )
    username_attempt = models.CharField(max_length=150, blank=True)
    successful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=10, choices=DEVICE_CHOICES, default='unknown')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    location_status = models.CharField(
        max_length=12,
        choices=LOCATION_STATUS_CHOICES,
        default='not_shared',
    )

    class Meta:
        verbose_name = 'Intento de inicio de sesión'
        verbose_name_plural = 'Intentos de inicio de sesión'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username_attempt or 'Usuario desconocido'} - {self.created_at:%Y-%m-%d %H:%M:%S}"

