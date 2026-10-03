from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0022_validate_and_seed_cuentas'),
    ]

    operations = [
        migrations.AddField(
            model_name='despachocombustible',
            name='labor',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Labor'),
        ),
        migrations.AddField(
            model_name='despachocombustible',
            name='proveedor',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Proveedor'),
        ),
    ]