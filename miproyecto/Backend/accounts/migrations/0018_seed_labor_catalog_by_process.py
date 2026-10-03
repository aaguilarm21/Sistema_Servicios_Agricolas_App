from django.db import migrations


KEPT_LABORS = {
    '4161': ('Siembra de maíz en surcos', 'siembras'),
    '4168': ('Trasplante de plántulas', 'siembras'),
    '4162': ('Aplicación de fertilizante foliar', 'fertilizacion'),
    '4165': ('Riego por aspersión', 'riego'),
}

NEW_LABORS = [
    ('4169', 'Preparación de semillero', 'siembras'),
    ('4170', 'Siembra directa', 'siembras'),
    ('4171', 'Resiembra de cultivo', 'siembras'),
    ('4172', 'Aplicación de fertilizante al suelo', 'fertilizacion'),
    ('4173', 'Aplicación de abono orgánico', 'fertilizacion'),
    ('4174', 'Aplicación de fertilizante granulado', 'fertilizacion'),
    ('4175', 'Fertirriego', 'fertilizacion'),
    ('4176', 'Riego por goteo', 'riego'),
    ('4177', 'Riego por gravedad', 'riego'),
    ('4178', 'Riego de establecimiento', 'riego'),
    ('4179', 'Mantenimiento del sistema de riego', 'riego'),
]

REMOVED_LABORS = [
    ('4163', 'Control de malezas con herbicida'),
    ('4164', 'Cosecha manual'),
    ('4166', 'Poda y limpieza de cultivo'),
    ('4167', 'Aplicación de fungicida'),
    ('4169', 'Mantenimiento de maquinaria'),
    ('4170', 'Transporte de insumos'),
    ('4171', 'Limpieza de maquinaria pesada'),
]


def group_labor_catalog(apps, schema_editor):
    Labor = apps.get_model('accounts', 'Labor')
    database = schema_editor.connection.alias

    Labor.objects.using(database).exclude(codigo__in=KEPT_LABORS).delete()
    for codigo, (descripcion, proceso) in KEPT_LABORS.items():
        labor, _ = Labor.objects.using(database).get_or_create(
            codigo=codigo,
            defaults={'descripcion': descripcion, 'proceso': proceso},
        )
        if labor.proceso != proceso:
            labor.proceso = proceso
            labor.save(update_fields=['proceso'])

    Labor.objects.using(database).bulk_create([
        Labor(codigo=codigo, descripcion=descripcion, proceso=proceso)
        for codigo, descripcion, proceso in NEW_LABORS
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_alter_labor_options_labor_proceso'),
    ]

    operations = [
        migrations.RunPython(group_labor_catalog, migrations.RunPython.noop),
    ]
