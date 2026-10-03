"""
Configuración de rutas URL para el proyecto miproyecto.

La lista `urlpatterns` conecta las direcciones URL con las vistas. Consulta:
https://docs.djangoproject.com/en/6.0/topics/http/urls/

Ejemplos:
Vistas basadas en funciones:
    1. Importa una vista: from una_app import vistas
    2. Añade una ruta: path('', vistas.inicio, name='inicio')
Vistas basadas en clases:
    1. Importa la vista: from otra_app.vistas import Inicio
    2. Añade una ruta: path('', Inicio.as_view(), name='inicio')
Incluir otra configuración de rutas:
    1. Importa include: from django.urls import include, path
    2. Añade una ruta: path('ejemplo/', include('ejemplo.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views
from accounts.views import CustomLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('', views.home, name='home'),
    path('modulos/', views.modulos, name='modulos'),
    path('configuracion/', views.configuracion_catalogos, name='configuracion'),
    path('datos-registrados/', views.datos_registrados, name='datos_registrados'),
    path('registros/', views.registros_operativos, name='registros'),
    path('registros-data/', views.registros_operativos_data, name='registros_data'),
    path('validar-registro-operativo/', views.validar_registro_operativo, name='validar_registro_operativo'),
    path('registros/<int:registro_id>/editar/', views.editar_registro_operativo, name='editar_registro'),
    path('registros/<int:registro_id>/borrar/', views.borrar_registro_operativo, name='borrar_registro'),
    path('usuarios/', views.usuarios, name='usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/creados/', views.usuarios_creados, name='usuarios_creados'),
    path('firmas-autorizadas/', views.firmas_autorizadas, name='firmas_autorizadas'),
    path('operacion/', views.operacion, name='operacion'),
    path('operacion/<int:operacion_id>/estado/', views.cambiar_estado_operacion, name='cambiar_estado_operacion'),
    path('operacion/<int:operacion_id>/eliminar/', views.eliminar_operacion_programada, name='eliminar_operacion_programada'),
    path('reportes/', views.reportes, name='reportes'),
    path('indicadores/', views.indicadores, name='indicadores'),
    # Módulo: Combustibles (3 procesos)
    path('combustibles/despachos/', views.despacho_combustible, name='despacho_combustible'),
    path('combustibles/despachos/<int:despacho_id>/gestionar/', views.gestionar_despacho_combustible, name='gestionar_despacho_combustible'),
    path('combustibles/consumo/', views.consumo_combustible, name='consumo_combustible'),
    path('combustibles/tanques/', views.tanques_combustible, name='tanques_combustible'),
    # Módulo: Maquinaria y Mantenimiento (3 procesos)
    path('mantenimiento/ordenes/', views.ordenes_mantenimiento, name='ordenes_mantenimiento'),
    path('mantenimiento/ordenes/<int:orden_id>/estado/', views.cambiar_estado_orden_mantenimiento, name='cambiar_estado_orden_mantenimiento'),
    path('mantenimiento/horometros/', views.control_horometros, name='control_horometros'),
    path('mantenimiento/flota/', views.estado_maquinaria, name='estado_maquinaria'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
