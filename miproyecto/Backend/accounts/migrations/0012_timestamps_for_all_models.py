from django.db import migrations, models
from django.utils import timezone


UPDATED_MODELS = (
    'Labor',
    'Cuenta',
    'UnidadMedida',
    'Variedad',
    'TipoMaquina',
    'Marca',
    'Municipio',
    'Auxiliar',
    'RegistroOperativo',
    'FirmaAutorizada',
)


def backfill_timestamps(apps, schema_editor):
    database = schema_editor.connection.alias
    for model_name in UPDATED_MODELS:
        model = apps.get_model('accounts', model_name)
        model.objects.using(database).update(updated_at=models.F('created_at'))

    nombre_puesto = apps.get_model('accounts', 'NombrePuesto')
    now = timezone.now()
    nombre_puesto.objects.using(database).update(created_at=now, updated_at=now)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_firmaautorizada'),
    ]

    operations = [
        migrations.AddField(
            model_name='labor',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='cuenta',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='unidadmedida',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='nombrepuesto',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='nombrepuesto',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='variedad',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='tipomaquina',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='marca',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='municipio',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='auxiliar',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='registrooperativo',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='firmaautorizada',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.RunPython(backfill_timestamps, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='labor',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='cuenta',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='unidadmedida',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='nombrepuesto',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='nombrepuesto',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='variedad',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='tipomaquina',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='marca',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='municipio',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='auxiliar',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='registrooperativo',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='firmaautorizada',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]