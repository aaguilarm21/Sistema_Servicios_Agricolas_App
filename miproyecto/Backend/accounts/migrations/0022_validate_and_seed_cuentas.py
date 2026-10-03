from django.core.validators import RegexValidator
from django.db import migrations, models


CUENTAS_POR_PROCESO = [
    ('siembras', '522104100001', 'Siembras'),
    ('fertilizacion', '522104100002', 'Fertilización'),
    ('riego', '522104100003', 'Riego'),
]


def crear_cuentas(apps, schema_editor):
    Cuenta = apps.get_model('accounts', 'Cuenta')
    database = schema_editor.connection.alias
    for proceso, codigo, descripcion in CUENTAS_POR_PROCESO:
        Cuenta.objects.using(database).update_or_create(
            proceso=proceso,
            defaults={
                'codigo': codigo,
                'descripcion': descripcion,
                'tipo': 'Gasto',
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0021_auxiliares_administrativos_a_tractoristas'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cuenta',
            name='codigo',
            field=models.CharField(
                max_length=12,
                unique=True,
                validators=[RegexValidator(r'^[0-9]{12}$', 'El código de cuenta debe contener exactamente 12 dígitos.')],
                verbose_name='Codigo',
            ),
        ),
        migrations.RunPython(crear_cuentas, migrations.RunPython.noop),
    ]