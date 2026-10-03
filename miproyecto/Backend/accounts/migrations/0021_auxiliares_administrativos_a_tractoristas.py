from django.db import migrations
from django.utils import timezone


EMPLEADOS_A_ACTUALIZAR = [
    'Edilzar Obed Zepeda',
    'Sergio David Ruiz Maldonado',
    'Édgar Manuel López',
]


def actualizar_puestos(apps, schema_editor):
    database = schema_editor.connection.alias
    Empleado = apps.get_model('accounts', 'Empleado')
    Empleado.objects.using(database).filter(
        empleado__in=EMPLEADOS_A_ACTUALIZAR,
        nombre_puesto='Auxiliar Administrativo',
    ).update(nombre_puesto='Tractorista', updated_at=timezone.now())


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_seed_nombre_puestos'),
    ]

    operations = [
        migrations.RunPython(actualizar_puestos, migrations.RunPython.noop),
    ]