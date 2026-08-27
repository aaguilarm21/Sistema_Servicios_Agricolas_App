from django.db import migrations, models


def normalize_existing_second_surnames(apps, schema_editor):
    Empleado = apps.get_model('accounts', 'Empleado')
    Empleado.objects.filter(segundo_apellido__isnull=True).update(segundo_apellido='')


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_add_segundo_apellido_to_empleado'),
    ]

    operations = [
        migrations.RunPython(
            normalize_existing_second_surnames,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='empleado',
            name='segundo_apellido',
            field=models.CharField(max_length=100, verbose_name='Segundo Apellido'),
        ),
    ]
