from django.contrib import admin
from .models import UserProfile, Proveedor, Empleado, RegistroOperativo


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'codigo', 'puesto', 'created_at')
    search_fields = ('codigo', 'usuario__username')
    ordering = ('-created_at',)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'razon_social', 'nit', 'regimen_tributario')
    search_fields = ('codigo', 'razon_social', 'nit')
    list_filter = ('regimen_tributario', 'created_at')
    ordering = ('-created_at',)


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'empresa', 'nombre_puesto', 'no_cui')
    search_fields = ('empleado', 'empresa', 'no_cui')
    list_filter = ('empresa', 'created_at')
    ordering = ('-created_at',)


@admin.register(RegistroOperativo)
class RegistroOperativoAdmin(admin.ModelAdmin):
    list_display = ('no_boleta', 'fecha_labor', 'tipo_servicio', 'proveedor', 'finca', 'lote', 'operador', 'created_at')
    
    search_fields = ('no_boleta', 'proveedor', 'finca', 'lote', 'operador', 'codigo_maquina')
    
    list_filter = ('fecha_labor', 'tipo_servicio', 'finca', 'created_at')
    
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('📝 ENCABEZADO', {
            'fields': ('no_boleta', 'fecha_labor', 'tipo_servicio')
        }),
        ('🚗 PROVEEDOR Y MÁQUINA', {
            'fields': ('proveedor', 'codigo_maquina', 'placa', 'operador')
        }),
        ('🌾 DETALLE FINCA Y LOTE', {
            'fields': ('finca', 'lote', 'area_lote', 'labor', 'corte_semilla')
        }),
        ('💰 FORMA DE PAGO', {
            'fields': ('unidades', 'horometro_inicial', 'horometro_final', 'costo_unitario', 'num_factura', 'cuenta_contable')
        }),
        ('🌱 DETALLES DE CAÑA', {
            'fields': ('variedad', 'total_paquetes', 'peso_kg')
        }),
        ('👥 SUPERVISORES', {
            'fields': ('caporal_01', 'caporal_02', 'mayordomo', 'administrador')
        }),
        ('📍 TRANSPORTE', {
            'fields': ('lugar_origen', 'lugar_destino')
        }),
        ('📋 OBSERVACIONES', {
            'fields': ('observaciones',)
        }),
        ('⏰ METADATA', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['delete_selected']
    
    def has_add_permission(self, request):
        # Permitir agregar registros desde el admin
        return True
    
    def has_change_permission(self, request, obj=None):
        # Permitir editar registros
        return True
    
    def has_delete_permission(self, request, obj=None):
        # Permitir eliminar registros
        return True
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
