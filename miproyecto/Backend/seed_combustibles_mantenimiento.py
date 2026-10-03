import os
import sys
from decimal import Decimal
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuraciones.miproyecto.settings')
import django
django.setup()

from accounts.models import (
    TanqueCombustible, DespachoCombustible, OrdenMantenimiento,
    ControlServicioHorometro, DisponibilidadMaquinaria, Maquinaria, Empleado
)

# 1. Tanques de Combustible
tanques_data = [
    {
        'codigo': 'TQ-01',
        'nombre': 'Tanque Principal Central',
        'tipo_combustible': 'Diésel',
        'capacidad_galones': Decimal('5000.00'),
        'nivel_actual_galones': Decimal('3850.00'),
        'ubicacion': 'Patio Central de Maquinaria',
        'estado': 'Operativo',
    },
    {
        'codigo': 'TQ-02',
        'nombre': 'Cisterna Móvil Campo 01',
        'tipo_combustible': 'Diésel',
        'capacidad_galones': Decimal('1500.00'),
        'nivel_actual_galones': Decimal('920.00'),
        'ubicacion': 'Finca El Carmen / Sector Lotes Caña',
        'estado': 'Operativo',
    },
    {
        'codigo': 'TQ-03',
        'nombre': 'Estación Auxiliar Gasolina',
        'tipo_combustible': 'Gasolina Regular',
        'capacidad_galones': Decimal('1000.00'),
        'nivel_actual_galones': Decimal('640.00'),
        'ubicacion': 'Taller Mecánico y Bombas',
        'estado': 'Operativo',
    },
    {
        'codigo': 'TQ-04',
        'nombre': 'Cisterna Móvil Campo 02',
        'tipo_combustible': 'Diésel',
        'capacidad_galones': Decimal('1500.00'),
        'nivel_actual_galones': Decimal('1200.00'),
        'ubicacion': 'Finca Santa Rosa / Frente de Siembra',
        'estado': 'En Reserva',
    },
]

for t in tanques_data:
    TanqueCombustible.objects.update_or_create(codigo=t['codigo'], defaults=t)

print("Tanques creados/actualizados")

# 2. Despachos de Combustible
hoy = date.today()
despachos_data = [
    {
        'no_vale': 'VAL-2026-081',
        'fecha': hoy - timedelta(days=2),
        'codigo_maquina': 'M1001',
        'tipo_combustible': 'Diésel',
        'galones': Decimal('45.50'),
        'horometro_actual': Decimal('1240.50'),
        'operador': 'Luis Fernando López',
        'estacion_tanque': 'Tanque Principal Central',
        'finca': 'Finca El Carmen',
        'despachado_por': 'Jorge Andrés Mendoza',
        'observaciones': 'Tanque lleno para jornada de arado en lote 4.',
    },
    {
        'no_vale': 'VAL-2026-082',
        'fecha': hoy - timedelta(days=2),
        'codigo_maquina': 'M1002',
        'tipo_combustible': 'Diésel',
        'galones': Decimal('78.00'),
        'horometro_actual': Decimal('890.20'),
        'operador': 'Ricardo Estuardo Vásquez',
        'estacion_tanque': 'Cisterna Móvil Campo 01',
        'finca': 'Finca San Antonio',
        'despachado_por': 'Jorge Andrés Mendoza',
        'observaciones': 'Corte y cosecha mecanizada turno diurno.',
    },
    {
        'no_vale': 'VAL-2026-083',
        'fecha': hoy - timedelta(days=1),
        'codigo_maquina': 'M1005',
        'tipo_combustible': 'Diésel',
        'galones': Decimal('38.25'),
        'horometro_actual': Decimal('645.10'),
        'operador': 'Carlos Alberto Ramírez',
        'estacion_tanque': 'Tanque Principal Central',
        'finca': 'Finca El Paraíso',
        'despachado_por': 'Jorge Andrés Mendoza',
        'observaciones': 'Labor de siembra y transporte de insumos.',
    },
    {
        'no_vale': 'VAL-2026-084',
        'fecha': hoy,
        'codigo_maquina': 'M1009',
        'tipo_combustible': 'Diésel',
        'galones': Decimal('52.00'),
        'horometro_actual': Decimal('412.80'),
        'operador': 'Luis Fernando López',
        'estacion_tanque': 'Cisterna Móvil Campo 01',
        'finca': 'Finca Santa Rosa',
        'despachado_por': 'Jorge Andrés Mendoza',
        'observaciones': 'Fumigación y control de malezas en cañaveral.',
    },
    {
        'no_vale': 'VAL-2026-085',
        'fecha': hoy,
        'codigo_maquina': 'M1012',
        'tipo_combustible': 'Diésel',
        'galones': Decimal('65.00'),
        'horometro_actual': Decimal('320.00'),
        'operador': 'Ricardo Estuardo Vásquez',
        'estacion_tanque': 'Tanque Principal Central',
        'finca': 'Finca El Carmen',
        'despachado_por': 'Jorge Andrés Mendoza',
        'observaciones': 'Cosecha mecanizada en lote 7.',
    },
]

for d in despachos_data:
    DespachoCombustible.objects.update_or_create(no_vale=d['no_vale'], defaults=d)

print("Despachos creados/actualizados")

# 3. Órdenes de Mantenimiento
ordenes_data = [
    {
        'codigo_orden': 'OT-2026-012',
        'fecha_ingreso': hoy - timedelta(days=5),
        'codigo_maquina': 'M1010',
        'tipo_mantenimiento': 'Preventivo',
        'prioridad': 'Media',
        'estado': 'En Taller',
        'mecanico': 'Jorge Andrés Mendoza',
        'horometro': Decimal('750.00'),
        'falla_reportada': 'Servicio preventivo de 750 horas: cambio de aceite motor, filtro combustible y filtro aire.',
        'trabajos_realizados': 'Drenado de aceite, instalación de filtros nuevos. Pendiente prueba hidrostática.',
        'costo_estimado': Decimal('1850.00'),
        'fecha_entrega': hoy + timedelta(days=1),
    },
    {
        'codigo_orden': 'OT-2026-013',
        'fecha_ingreso': hoy - timedelta(days=3),
        'codigo_maquina': 'M1007',
        'tipo_mantenimiento': 'Correctivo',
        'prioridad': 'Alta',
        'estado': 'En Taller',
        'mecanico': 'Jorge Andrés Mendoza',
        'horometro': Decimal('1420.50'),
        'falla_reportada': 'Fuga de aceite hidráulico en manguera de cilindro de elevación de cuchilla.',
        'trabajos_realizados': 'Desmontaje de línea averiada, reemplazo de racores y manguera de alta presión.',
        'costo_estimado': Decimal('2400.00'),
        'fecha_entrega': hoy,
    },
    {
        'codigo_orden': 'OT-2026-014',
        'fecha_ingreso': hoy - timedelta(days=1),
        'codigo_maquina': 'M1003',
        'tipo_mantenimiento': 'Rutinario',
        'prioridad': 'Baja',
        'estado': 'Pendiente',
        'mecanico': 'Fernando José Torres',
        'horometro': Decimal('530.00'),
        'falla_reportada': 'Engrase general y cambio de tornillería en soporte de discos de arado.',
        'trabajos_realizados': 'Inspección preliminar realizada.',
        'costo_estimado': Decimal('650.00'),
        'fecha_entrega': hoy + timedelta(days=2),
    },
    {
        'codigo_orden': 'OT-2026-010',
        'fecha_ingreso': hoy - timedelta(days=10),
        'codigo_maquina': 'M1001',
        'tipo_mantenimiento': 'Preventivo',
        'prioridad': 'Normal',
        'estado': 'Finalizada',
        'mecanico': 'Jorge Andrés Mendoza',
        'horometro': Decimal('1200.00'),
        'falla_reportada': 'Calibración de frenos y cambio de filtro de cabina.',
        'trabajos_realizados': 'Calibración concluida con éxito, unidad entregada a campo.',
        'costo_estimado': Decimal('1200.00'),
        'fecha_entrega': hoy - timedelta(days=8),
    },
]

for o in ordenes_data:
    OrdenMantenimiento.objects.update_or_create(codigo_orden=o['codigo_orden'], defaults=o)

print("Órdenes de mantenimiento creadas/actualizadas")

# 4. Control de Servicios por Horómetro
servicios_data = [
    {
        'codigo_maquina': 'M1001',
        'tipo_servicio': 'Servicio 250 Horas (Aceite y Filtros)',
        'intervalo_horas': 250,
        'ultimo_horometro': Decimal('1000.00'),
        'proximo_horometro': Decimal('1250.00'),
        'horometro_actual': Decimal('1240.50'),
        'estado_alerta': 'Próximo a Vencer',
        'fecha_ultimo_servicio': hoy - timedelta(days=45),
        'observaciones': 'Faltan 9.5 horas para el próximo cambio de aceite.',
    },
    {
        'codigo_maquina': 'M1002',
        'tipo_servicio': 'Servicio 500 Horas (Sistema Hidráulico y Refrigerante)',
        'intervalo_horas': 500,
        'ultimo_horometro': Decimal('500.00'),
        'proximo_horometro': Decimal('1000.00'),
        'horometro_actual': Decimal('890.20'),
        'estado_alerta': 'Al Día',
        'fecha_ultimo_servicio': hoy - timedelta(days=60),
        'observaciones': 'Operación normal, próxima revisión programada a 1,000h.',
    },
    {
        'codigo_maquina': 'M1007',
        'tipo_servicio': 'Servicio 250 Horas (Engrase y Filtro Combustible)',
        'intervalo_horas': 250,
        'ultimo_horometro': Decimal('1150.00'),
        'proximo_horometro': Decimal('1400.00'),
        'horometro_actual': Decimal('1420.50'),
        'estado_alerta': 'Vencido',
        'fecha_ultimo_servicio': hoy - timedelta(days=90),
        'observaciones': 'Sobrepasó el límite por 20.5 horas. En taller actualmente.',
    },
    {
        'codigo_maquina': 'M1005',
        'tipo_servicio': 'Servicio 250 Horas (Aceite y Filtros)',
        'intervalo_horas': 250,
        'ultimo_horometro': Decimal('500.00'),
        'proximo_horometro': Decimal('750.00'),
        'horometro_actual': Decimal('645.10'),
        'estado_alerta': 'Al Día',
        'fecha_ultimo_servicio': hoy - timedelta(days=30),
        'observaciones': 'En servicio óptimo de labor.',
    },
    {
        'codigo_maquina': 'M1009',
        'tipo_servicio': 'Servicio 250 Horas (Calibración Bombas y Boquillas)',
        'intervalo_horas': 250,
        'ultimo_horometro': Decimal('200.00'),
        'proximo_horometro': Decimal('450.00'),
        'horometro_actual': Decimal('412.80'),
        'estado_alerta': 'Próximo a Vencer',
        'fecha_ultimo_servicio': hoy - timedelta(days=35),
        'observaciones': 'Monitorear presión de aspersión en campo.',
    },
]

for s in servicios_data:
    ControlServicioHorometro.objects.update_or_create(
        codigo_maquina=s['codigo_maquina'],
        tipo_servicio=s['tipo_servicio'],
        defaults=s
    )

print("Controles de servicio por horómetro creados/actualizados")

# 5. Disponibilidad de Maquinaria
flota_data = [
    {'codigo_maquina': 'M1001', 'estado': 'En Campo', 'finca_actual': 'Finca El Carmen', 'operador_asignado': 'Luis Fernando López', 'horometro_actual': Decimal('1240.50')},
    {'codigo_maquina': 'M1002', 'estado': 'En Campo', 'finca_actual': 'Finca San Antonio', 'operador_asignado': 'Ricardo Estuardo Vásquez', 'horometro_actual': Decimal('890.20')},
    {'codigo_maquina': 'M1003', 'estado': 'Disponible', 'finca_actual': 'Patio Central', 'operador_asignado': 'Sin asignar', 'horometro_actual': Decimal('530.00')},
    {'codigo_maquina': 'M1004', 'estado': 'Disponible', 'finca_actual': 'Patio Central', 'operador_asignado': 'Sin asignar', 'horometro_actual': Decimal('180.00')},
    {'codigo_maquina': 'M1005', 'estado': 'En Campo', 'finca_actual': 'Finca El Paraíso', 'operador_asignado': 'Carlos Alberto Ramírez', 'horometro_actual': Decimal('645.10')},
    {'codigo_maquina': 'M1006', 'estado': 'Disponible', 'finca_actual': 'Patio Central', 'operador_asignado': 'Sin asignar', 'horometro_actual': Decimal('310.40')},
    {'codigo_maquina': 'M1007', 'estado': 'En Taller', 'finca_actual': 'Taller Central', 'operador_asignado': 'Jorge Andrés Mendoza', 'horometro_actual': Decimal('1420.50')},
    {'codigo_maquina': 'M1008', 'estado': 'Disponible', 'finca_actual': 'Patio Central', 'operador_asignado': 'Sin asignar', 'horometro_actual': Decimal('90.00')},
    {'codigo_maquina': 'M1009', 'estado': 'En Campo', 'finca_actual': 'Finca Santa Rosa', 'operador_asignado': 'Luis Fernando López', 'horometro_actual': Decimal('412.80')},
    {'codigo_maquina': 'M1010', 'estado': 'En Taller', 'finca_actual': 'Taller Central', 'operador_asignado': 'Jorge Andrés Mendoza', 'horometro_actual': Decimal('750.00')},
    {'codigo_maquina': 'M1011', 'estado': 'Disponible', 'finca_actual': 'Patio Central', 'operador_asignado': 'Sin asignar', 'horometro_actual': Decimal('120.00')},
    {'codigo_maquina': 'M1012', 'estado': 'En Campo', 'finca_actual': 'Finca El Carmen', 'operador_asignado': 'Ricardo Estuardo Vásquez', 'horometro_actual': Decimal('320.00')},
]

for f in flota_data:
    DisponibilidadMaquinaria.objects.update_or_create(codigo_maquina=f['codigo_maquina'], defaults=f)

print("Disponibilidad de flota creada/actualizada")
