content = """

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
        return f\"{self.codigo} - {self.descripcion}\"


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
        return f\"{self.codigo} - {self.descripcion}\"


class UnidadMedida(models.Model):
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Codigo')
    descripcion = models.CharField(max_length=150, verbose_name='Descripcion')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'
        ordering = ['codigo']

    def __str__(self):
        return f\"{self.codigo} - {self.descripcion}\"


class Variedad(models.Model):
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Codigo')
    descripcion = models.CharField(max_length=200, verbose_name='Descripcion')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Variedad'
        verbose_name_plural = 'Variedades'
        ordering = ['codigo']

    def __str__(self):
        return f\"{self.codigo} - {self.descripcion}\"


class TipoMaquina(models.Model):
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Codigo')
    descripcion = models.CharField(max_length=200, verbose_name='Descripcion')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tipo de Maquina'
        verbose_name_plural = 'Tipos de Maquina'
        ordering = ['codigo']

    def __str__(self):
        return f\"{self.codigo} - {self.descripcion}\"


class Marca(models.Model):
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Codigo')
    descripcion = models.CharField(max_length=200, verbose_name='Descripcion')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['codigo']

    def __str__(self):
        return f\"{self.codigo} - {self.descripcion}\"


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
        return f\"{self.codigo} - {self.nombre}\"


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
        return f\"{self.codigo} - {self.nombre}\"
"""

with open(r'accounts/models.py', 'a', encoding='utf-8') as f:
    f.write(content)
print('Modelos agregados correctamente')
