from django.urls import path
from .views import (
    ajax_login, signup, buscar_usuario_por_codigo,
    api_proveedores, api_proveedor_detalle,
    api_empleados, api_empleado_detalle,
    api_usuario,
    api_maquinaria, api_maquinaria_detalle,
    api_bodegas, api_bodega_detalle,
    api_articulos, api_articulo_detalle,
    # Catálogos auxiliares
    api_labores, api_labor_detalle,
    api_cuentas, api_cuenta_detalle,
    api_unidades, api_unidad_detalle,
    api_variedades, api_variedad_detalle,
    api_tipos_maquina, api_tipo_maquina_detalle,
    api_marcas, api_marca_detalle,
    api_municipios, api_municipio_detalle,
    api_auxiliares, api_auxiliar_detalle,
)

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('ajax-login/', ajax_login, name='ajax_login'),
    path('api/buscar-usuario/', buscar_usuario_por_codigo, name='buscar_usuario'),

    path('api/proveedores/', api_proveedores, name='api_proveedores'),
    path('api/proveedores/<int:proveedor_id>/', api_proveedor_detalle, name='api_proveedor_detalle'),

    path('api/empleados/', api_empleados, name='api_empleados'),
    path('api/empleados/<int:empleado_id>/', api_empleado_detalle, name='api_empleado_detalle'),
    path('api/usuarios/<int:user_id>/', api_usuario, name='api_usuario'),

    path('api/maquinaria/', api_maquinaria, name='api_maquinaria'),
    path('api/maquinaria/<int:maquinaria_id>/', api_maquinaria_detalle, name='api_maquinaria_detalle'),

    path('api/bodegas/', api_bodegas, name='api_bodegas'),
    path('api/bodegas/<int:bodega_id>/', api_bodega_detalle, name='api_bodega_detalle'),

    path('api/articulos/', api_articulos, name='api_articulos'),
    path('api/articulos/<int:articulo_id>/', api_articulo_detalle, name='api_articulo_detalle'),

    # Catálogos auxiliares
    path('api/labores/', api_labores, name='api_labores'),
    path('api/labores/<int:pk>/', api_labor_detalle, name='api_labor_detalle'),

    path('api/cuentas/', api_cuentas, name='api_cuentas'),
    path('api/cuentas/<int:pk>/', api_cuenta_detalle, name='api_cuenta_detalle'),

    path('api/unidades/', api_unidades, name='api_unidades'),
    path('api/unidades/<int:pk>/', api_unidad_detalle, name='api_unidad_detalle'),

    path('api/variedades/', api_variedades, name='api_variedades'),
    path('api/variedades/<int:pk>/', api_variedad_detalle, name='api_variedad_detalle'),

    path('api/tipos-maquina/', api_tipos_maquina, name='api_tipos_maquina'),
    path('api/tipos-maquina/<int:pk>/', api_tipo_maquina_detalle, name='api_tipo_maquina_detalle'),

    path('api/marcas/', api_marcas, name='api_marcas'),
    path('api/marcas/<int:pk>/', api_marca_detalle, name='api_marca_detalle'),

    path('api/municipios/', api_municipios, name='api_municipios'),
    path('api/municipios/<int:pk>/', api_municipio_detalle, name='api_municipio_detalle'),

    path('api/auxiliares/', api_auxiliares, name='api_auxiliares'),
    path('api/auxiliares/<int:pk>/', api_auxiliar_detalle, name='api_auxiliar_detalle'),
]
