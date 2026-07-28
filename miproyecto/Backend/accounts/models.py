from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
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


class Proveedor(models.Model):
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


class Empleado(models.Model):
    empresa = models.CharField(max_length=200, verbose_name='Empresa')
    empleado = models.CharField(max_length=150, verbose_name='Empleado')
    no_cui = models.CharField(max_length=20, verbose_name='No. CUI')
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


class Maquinaria(models.Model):
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


class Bodega(models.Model):
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


class Articulo(models.Model):
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

class Labor(models.Model):
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Codigo')
    descripcion = models.CharField(max_length=200, verbose_name='Descripcion')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Labor'
        verbose_name_plural = 'Labores'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


class Cuenta(models.Model):
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Codigo')
    descripcion = models.CharField(max_length=200, verbose_name='Descripcion')
    tipo = models.CharField(max_length=100, verbose_name='Tipo', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


class UnidadMedida(models.Model):
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Codigo')
    descripcion = models.CharField(max_length=150, verbose_name='Descripcion')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


class Variedad(models.Model):
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Codigo')
    descripcion = models.CharField(max_length=200, verbose_name='Descripcion')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Variedad'
        verbose_name_plural = 'Variedades'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


class TipoMaquina(models.Model):
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Codigo')
    descripcion = models.CharField(max_length=200, verbose_name='Descripcion')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tipo de Maquina'
        verbose_name_plural = 'Tipos de Maquina'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


class Marca(models.Model):
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Codigo')
    descripcion = models.CharField(max_length=200, verbose_name='Descripcion')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


class Municipio(models.Model):
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Codigo')
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    departamento = models.CharField(max_length=150, verbose_name='Departamento', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Municipio'
        verbose_name_plural = 'Municipios'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Auxiliar(models.Model):
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Codigo')
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    tipo = models.CharField(max_length=100, verbose_name='Tipo', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Auxiliar'
        verbose_name_plural = 'Auxiliares'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class RegistroOperativo(models.Model):
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

    class Meta:
        verbose_name = 'Registro Operativo'
        verbose_name_plural = 'Registros Operativos'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.no_boleta} - {self.fecha_labor}"
