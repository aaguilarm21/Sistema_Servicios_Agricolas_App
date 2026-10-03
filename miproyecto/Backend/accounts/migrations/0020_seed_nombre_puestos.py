from django.db import migrations
from django.utils import timezone


NOMBRES_PUESTO = [
    'Piloto',
    'Mecanico',
    'Chofer',
    'Auxiliar Administrativo',
    'Tractorista',
    'Labores Agricolas',
]

MAPEO_PUESTOS = {
    'operador de cosechadora': 'Piloto',
    'mecánico agrícola': 'Mecanico',
    'auxiliar de taller': 'Mecanico',
    'chofer de maquinaria': 'Chofer',
    'asistente administrativo': 'Auxiliar Administrativo',
    'asistente de compras': 'Auxiliar Administrativo',
    'coordinadora de logística': 'Auxiliar Administrativo',
    'encargada de inventarios': 'Auxiliar Administrativo',
    'ingeniero en sistemas': 'Auxiliar Administrativo',
    'jefe de oficina': 'Auxiliar Administrativo',
    'supervisor de campo': 'Auxiliar Administrativo',
    'supervisor de maquinaria': 'Auxiliar Administrativo',
    'operador de tractor': 'Tractorista',
    'auxiliar de campo': 'Labores Agricolas',
    'labores agricolas': 'Labores Agricolas',
}


def crear_puestos_y_actualizar_empleados(apps, schema_editor):
    database = schema_editor.connection.alias
    NombrePuesto = apps.get_model('accounts', 'NombrePuesto')
    Empleado = apps.get_model('accounts', 'Empleado')

    for nombre in NOMBRES_PUESTO:
        existe = NombrePuesto.objects.using(database).filter(nombre__iexact=nombre).exists()
        if not existe:
            NombrePuesto.objects.using(database).create(nombre=nombre)

    for empleado in Empleado.objects.using(database).all().only('id', 'nombre_puesto'):
        nombre_actual = (empleado.nombre_puesto or '').strip().casefold()
        nombre_nuevo = MAPEO_PUESTOS.get(nombre_actual)
        if nombre_nuevo and empleado.nombre_puesto != nombre_nuevo:
            Empleado.objects.using(database).filter(pk=empleado.pk).update(
                nombre_puesto=nombre_nuevo,
                updated_at=timezone.now(),
            )


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0019_cuenta_proceso'),
    ]

    operations = [
        migrations.RunPython(crear_puestos_y_actualizar_empleados, migrations.RunPython.noop),
    ]