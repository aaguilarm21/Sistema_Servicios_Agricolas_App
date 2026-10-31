from django.core.cache import cache


MODULE_CATALOG_CACHE_PREFIX = 'accounts:module_catalog:'
MODULE_CATALOG_CACHE_TIMEOUT = 60

NOMBRES_CACHE_CATALOGO_POR_MODELO = {
    'accounts.auxiliar': ('fincas',),
    'accounts.cuenta': ('cuentas_por_proceso',),
    'accounts.empleado': ('empleados', 'mecanicos'),
    'accounts.firmaautorizada': ('firmas_autorizadas',),
    'accounts.labor': ('labores',),
    'accounts.maquinaria': ('maquinarias',),
    'accounts.municipio': ('municipios',),
    'accounts.proveedor': ('proveedores',),
    'accounts.tanquecombustible': ('tanques_combustible',),
    'accounts.variedad': ('variedades',),
}


def catalogo_modulo_en_cache(nombre, consulta):
    clave_cache = f'{MODULE_CATALOG_CACHE_PREFIX}{nombre}'
    catalogo = cache.get(clave_cache)
    if catalogo is None:
        catalogo = list(consulta)
        cache.set(clave_cache, catalogo, timeout=MODULE_CATALOG_CACHE_TIMEOUT)
    return catalogo


def invalidar_cache_catalogo_modulo(sender, **kwargs):
    etiqueta_modelo = sender._meta.label_lower
    for nombre in NOMBRES_CACHE_CATALOGO_POR_MODELO.get(etiqueta_modelo, ()):
        cache.delete(f'{MODULE_CATALOG_CACHE_PREFIX}{nombre}')
