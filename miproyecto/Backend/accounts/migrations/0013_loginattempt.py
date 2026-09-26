import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_timestamps_for_all_models'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username_attempt', models.CharField(blank=True, max_length=150)),
                ('successful', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('device_type', models.CharField(choices=[('mobile', 'Móvil'), ('tablet', 'Tableta'), ('pc', 'PC'), ('unknown', 'Desconocido')], default='unknown', max_length=10)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('location_status', models.CharField(choices=[('captured', 'GPS capturado'), ('not_shared', 'No compartida'), ('denied', 'Permiso denegado'), ('unavailable', 'No disponible')], default='not_shared', max_length=12)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='login_attempts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Intento de inicio de sesión',
                'verbose_name_plural': 'Intentos de inicio de sesión',
                'ordering': ['-created_at'],
            },
        ),
    ]