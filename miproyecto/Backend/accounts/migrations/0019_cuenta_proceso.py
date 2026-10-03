from django.db import migrations, models


def vaciar_catalogo_cuentas(apps, schema_editor):
    Cuenta = apps.get_model('accounts', 'Cuenta')
    Cuenta.objects.using(schema_editor.connection.alias).all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_seed_labor_catalog_by_process'),
    ]

    operations = [
        migrations.RunPython(vaciar_catalogo_cuentas, migrations.RunPython.noop),
        migrations.AddField(
            model_name='cuenta',
            name='proceso',
            field=models.CharField(
                choices=[
                    ('siembras', 'Siembras'),
                    ('fertilizacion', 'Fertilización'),
                    ('riego', 'Riego'),
                ],
                max_length=20,
                unique=True,
                verbose_name='Proceso',
            ),
        ),
        migrations.AlterModelOptions(
            name='cuenta',
            options={
                'ordering': ['proceso'],
                'verbose_name': 'Cuenta',
                'verbose_name_plural': 'Cuentas',
            },
        ),
        migrations.AddConstraint(
            model_name='cuenta',
            constraint=models.CheckConstraint(
                condition=models.Q(proceso__in=['siembras', 'fertilizacion', 'riego']),
                name='cuenta_proceso_valido',
            ),
        ),
    ]