"""
URL configuration for miproyecto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

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
    path('registros/', views.registros_operativos, name='registros'),
    path('registros-data/', views.registros_operativos_data, name='registros_data'),
    path('registros/<int:registro_id>/editar/', views.editar_registro_operativo, name='editar_registro'),
    path('registros/<int:registro_id>/borrar/', views.borrar_registro_operativo, name='borrar_registro'),
    path('usuarios/', views.usuarios, name='usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/creados/', views.usuarios_creados, name='usuarios_creados'),
    path('operacion/', views.operacion, name='operacion'),
    path('reportes/', views.reportes, name='reportes'),
]
