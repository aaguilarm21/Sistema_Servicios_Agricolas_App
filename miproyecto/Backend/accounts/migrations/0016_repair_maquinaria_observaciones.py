from django.db import migrations


def repair_maquinaria_observaciones(apps, schema_editor):
    maquinaria = apps.get_model('accounts', 'Maquinaria')
    table_name = maquinaria._meta.db_table

    with schema_editor.connection.cursor() as cursor:
        columns = {
            column.name
            for column in schema_editor.connection.introspection.get_table_description(
                cursor,
                table_name,
            )
        }

    if 'observaciones' not in columns:
        schema_editor.add_field(
            maquinaria,
            maquinaria._meta.get_field('observaciones'),
        )


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0015_registrooperativo_finca_corte_semilla_and_more'),
    ]

    operations = [
        migrations.RunPython(
            repair_maquinaria_observaciones,
            migrations.RunPython.noop,
        ),
    ]