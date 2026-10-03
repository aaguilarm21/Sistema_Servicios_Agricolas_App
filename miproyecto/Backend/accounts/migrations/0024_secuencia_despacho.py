from datetime import date

from django.db import migrations, models


def crear_secuencia_inicial(apps, schema_editor):
    database = schema_editor.connection.alias
    Despacho = apps.get_model('accounts', 'DespachoCombustible')
    Secuencia = apps.get_model('accounts', 'SecuenciaDespacho')
    anio = date.today().year
    prefijo = f'VAL-{anio}-'
    ultimo = max(
        (
            int(valor[len(prefijo):])
            for valor in Despacho.objects.using(database).filter(
                no_vale__startswith=prefijo
            ).values_list('no_vale', flat=True)
            if valor[len(prefijo):].isdigit()
        ),
        default=0,
    )
    Secuencia.objects.using(database).update_or_create(
        pk=1,
        defaults={'anio': anio, 'ultimo_numero': ultimo},
    )


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0023_despacho_proveedor_labor'),
    ]

    operations = [
        migrations.CreateModel(
            name='SecuenciaDespacho',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('anio', models.PositiveSmallIntegerField(verbose_name='Año')),
                ('ultimo_numero', models.PositiveIntegerField(default=0, verbose_name='Último correlativo')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Secuencia de despacho',
                'verbose_name_plural': 'Secuencias de despachos',
            },
        ),
        migrations.RunPython(crear_secuencia_inicial, migrations.RunPython.noop),
    ]