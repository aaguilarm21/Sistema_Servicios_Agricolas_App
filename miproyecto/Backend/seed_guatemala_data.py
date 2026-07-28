import os
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miproyecto.settings')
django.setup()

from accounts.models import Proveedor, Empleado, Maquinaria, Labor, Cuenta, UnidadMedida, Variedad, TipoMaquina, Marca, Municipio, Auxiliar

proveedores = [
    {'codigo': '10001', 'nit': '2065487120115', 'razon_social': 'Agroservicios Peteneros, S.A.', 'nombre_propietario': 'Juan Carlos Pérez', 'regimen_tributario': 'General', 'tipo_factura': 'Factura Electrónica (FEL)', 'dias_credito': 30},
    {'codigo': '10002', 'nit': '3498812100115', 'razon_social': 'Agroindustrias del Sur', 'nombre_propietario': 'María Elena Cifuentes', 'regimen_tributario': 'Pequeño Contribuyente', 'tipo_factura': 'Factura Electrónica (FEL)', 'dias_credito': 15},
    {'codigo': '10003', 'nit': '1675024130117', 'razon_social': 'Fertilizantes y Servicios Guatemala', 'nombre_propietario': 'Carlos Eduardo Morales', 'regimen_tributario': 'General', 'tipo_factura': 'Factura Electrónica (FEL)', 'dias_credito': 60},
    {'codigo': '10004', 'nit': '3487920150113', 'razon_social': 'Corredores Agrícolas del Norte', 'nombre_propietario': 'Ana Sofía López', 'regimen_tributario': 'Pequeño Contribuyente', 'tipo_factura': 'Factura Electrónica (FEL)', 'dias_credito': 20},
    {'codigo': '10005', 'nit': '5893167200114', 'razon_social': 'Corporación Agrícola Alta Verapaz', 'nombre_propietario': 'Roberto Miguel Ortiz', 'regimen_tributario': 'General', 'tipo_factura': 'Factura Electrónica (FEL)', 'dias_credito': 45},
    {'codigo': '10006', 'nit': '1186529340116', 'razon_social': 'Distribuidora Campesina', 'nombre_propietario': 'Leticia Marisol Ramírez', 'regimen_tributario': 'Pequeño Contribuyente', 'tipo_factura': 'Factura Electrónica (FEL)', 'dias_credito': 10},
    {'codigo': '10007', 'nit': '5264190830112', 'razon_social': 'Agroinsumos Santa Rosa', 'nombre_propietario': 'Miguel Ángel Hernández', 'regimen_tributario': 'General', 'tipo_factura': 'Factura Electrónica (FEL)', 'dias_credito': 30},
    {'codigo': '10008', 'nit': '7392841560118', 'razon_social': 'Soluciones Agrícolas del Oriente', 'nombre_propietario': 'Isabel Patricia Cruz', 'regimen_tributario': 'Pequeño Contribuyente', 'tipo_factura': 'Factura Electrónica (FEL)', 'dias_credito': 25},
    {'codigo': '10009', 'nit': '2796018450114', 'razon_social': 'Maquinaria Campo Verde', 'nombre_propietario': 'José Manuel Díaz', 'regimen_tributario': 'General', 'tipo_factura': 'Factura Electrónica (FEL)', 'dias_credito': 40},
    {'codigo': '10010', 'nit': '4791038250118', 'razon_social': 'Insumos del Altiplano', 'nombre_propietario': 'Gloria Teresa Méndez', 'regimen_tributario': 'Pequeño Contribuyente', 'tipo_factura': 'Factura Electrónica (FEL)', 'dias_credito': 15},
    {'codigo': '10011', 'nit': '2045687130111', 'razon_social': 'Servicios Agropecuarios del Pacífico', 'nombre_propietario': 'Fernando Javier Santos', 'regimen_tributario': 'General', 'tipo_factura': 'Factura Electrónica (FEL)', 'dias_credito': 30},
    {'codigo': '10012', 'nit': '3201457890119', 'razon_social': 'Distribuciones del Ixim', 'nombre_propietario': 'María Paula Méndez', 'regimen_tributario': 'Pequeño Contribuyente', 'tipo_factura': 'Factura Electrónica (FEL)', 'dias_credito': 20},
]

empleados = [
    {'empresa': 'Inversiones Agricolas Febrero, S. A.', 'empleado': 'Luis Fernando López', 'no_cui': '3000101234567', 'puesto': '3090', 'nombre_puesto': 'Operador de Tractor'},
    {'empresa': 'Inversiones Agricolas Febrero, S. A.', 'empleado': 'Ana María Pacheco', 'no_cui': '3789723456789', 'puesto': '4125', 'nombre_puesto': 'Auxiliar de Campo'},
    {'empresa': 'Inversiones Agricolas Febrero, S. A.', 'empleado': 'Carlos Alberto Ramírez', 'no_cui': '3620149876543', 'puesto': '4150', 'nombre_puesto': 'Chofer de Maquinaria'},
    {'empresa': 'Inversiones Agricolas Febrero, S. A.', 'empleado': 'María Elena García', 'no_cui': '4020158765432', 'puesto': '4210', 'nombre_puesto': 'Supervisor de Campo'},
    {'empresa': 'Inversiones Agricolas Febrero, S. A.', 'empleado': 'Jorge Andrés Mendoza', 'no_cui': '3020145678901', 'puesto': '3300', 'nombre_puesto': 'Mecánico Agrícola'},
    {'empresa': 'Inversiones Agricolas Febrero, S. A.', 'empleado': 'Jessica Lorena Castillo', 'no_cui': '2998743210567', 'puesto': '3275', 'nombre_puesto': 'Asistente Administrativo'},
    {'empresa': 'Inversiones Agricolas Febrero, S. A.', 'empleado': 'Ricardo Estuardo Vásquez', 'no_cui': '3321987654321', 'puesto': '4180', 'nombre_puesto': 'Operador de Cosechadora'},
    {'empresa': 'Inversiones Agricolas Febrero, S. A.', 'empleado': 'Claudia Patricia Solís', 'no_cui': '3885601234790', 'puesto': '4300', 'nombre_puesto': 'Encargada de Inventarios'},
    {'empresa': 'Inversiones Agricolas Febrero, S. A.', 'empleado': 'Fernando José Torres', 'no_cui': '3200987123456', 'puesto': '3400', 'nombre_puesto': 'Auxiliar de Taller'},
    {'empresa': 'Inversiones Agricolas Febrero, S. A.', 'empleado': 'Yasmin Alejandra Ortiz', 'no_cui': '3165478901234', 'puesto': '4500', 'nombre_puesto': 'Coordinadora de Logística'},
    {'empresa': 'Inversiones Agricolas Febrero, S. A.', 'empleado': 'Édgar Manuel López', 'no_cui': '3147859021345', 'puesto': '4310', 'nombre_puesto': 'Supervisor de Maquinaria'},
    {'empresa': 'Inversiones Agricolas Febrero, S. A.', 'empleado': 'Sandra Patricia Hernández', 'no_cui': '3765890123456', 'puesto': '4400', 'nombre_puesto': 'Asistente de Compras'},
]

maquinaria = [
    {'codigo_maquina': 'M1001', 'combustible': 'Si', 'id_proveedor': '10009', 'tipo_maquina': 'tractor', 'marca_maquina': 'John Deere', 'serie_maquina': 'JD-4720-01', 'placa_matricula': 'P-043-TMP', 'observaciones': 'Mantenimiento al día.'},
    {'codigo_maquina': 'M1002', 'combustible': 'Si', 'id_proveedor': '10001', 'tipo_maquina': 'cosechadora', 'marca_maquina': 'Case IH', 'serie_maquina': 'CIH-6040-12', 'placa_matricula': 'P-064-GUA', 'observaciones': 'Usada en la zona de Chimaltenango.'},
    {'codigo_maquina': 'M1003', 'combustible': 'Si', 'id_proveedor': '10002', 'tipo_maquina': 'arado', 'marca_maquina': 'Plancorp', 'serie_maquina': 'PC-AR-201', 'placa_matricula': 'N/A', 'observaciones': 'Arado de discos doble.'},
    {'codigo_maquina': 'M1004', 'combustible': 'No', 'id_proveedor': '10003', 'tipo_maquina': 'sembradora', 'marca_maquina': 'Kuhn', 'serie_maquina': 'K-1200-33', 'placa_matricula': 'N/A', 'observaciones': 'Lista para siembra de maíz.'},
    {'codigo_maquina': 'M1005', 'combustible': 'Si', 'id_proveedor': '10004', 'tipo_maquina': 'tractor', 'marca_maquina': 'New Holland', 'serie_maquina': 'NH-T3040-09', 'placa_matricula': 'P-102-AGI', 'observaciones': 'Asignada a finca en Baja Verapaz.'},
    {'codigo_maquina': 'M1006', 'combustible': 'Si', 'id_proveedor': '10005', 'tipo_maquina': 'retroexcavadora', 'marca_maquina': 'Caterpillar', 'serie_maquina': 'CAT-432F-77', 'placa_matricula': 'P-215-MAQ', 'observaciones': 'Utilizada para drenajes.'},
    {'codigo_maquina': 'M1007', 'combustible': 'Si', 'id_proveedor': '10006', 'tipo_maquina': 'motoniveladora', 'marca_maquina': 'Volvo', 'serie_maquina': 'V-140G-05', 'placa_matricula': 'P-307-GTM', 'observaciones': 'Revisar sistema hidráulico.'},
    {'codigo_maquina': 'M1008', 'combustible': 'No', 'id_proveedor': '10007', 'tipo_maquina': 'remolque', 'marca_maquina': 'Titan', 'serie_maquina': 'TT-1500-22', 'placa_matricula': 'P-411-TRK', 'observaciones': 'Capacidad 8 toneladas.'},
    {'codigo_maquina': 'M1009', 'combustible': 'Si', 'id_proveedor': '10008', 'tipo_maquina': 'fumigadora', 'marca_maquina': 'Hardi', 'serie_maquina': 'HRD-300-18', 'placa_matricula': 'N/A', 'observaciones': 'Se usa en cultivos de caña.'},
    {'codigo_maquina': 'M1010', 'combustible': 'Si', 'id_proveedor': '10001', 'tipo_maquina': 'tractor', 'marca_maquina': 'Massey Ferguson', 'serie_maquina': 'MF-4707-13', 'placa_matricula': 'P-513-MF', 'observaciones': 'En mantenimiento preventivo.'},
    {'codigo_maquina': 'M1011', 'combustible': 'Si', 'id_proveedor': '10002', 'tipo_maquina': 'sembradora', 'marca_maquina': 'Monosem', 'serie_maquina': 'MS-300-04', 'placa_matricula': 'N/A', 'observaciones': 'Listo para temporada de frijol.'},
    {'codigo_maquina': 'M1012', 'combustible': 'Si', 'id_proveedor': '10009', 'tipo_maquina': 'cosechadora', 'marca_maquina': 'Claas', 'serie_maquina': 'CL-760-08', 'placa_matricula': 'P-625-CLC', 'observaciones': 'Nueva unidad en operativo.'},
]

labores = [
    {'codigo': '4161', 'descripcion': 'Siembra de maíz en surcos'},
    {'codigo': '4162', 'descripcion': 'Aplicación de fertilizante foliar'},
    {'codigo': '4163', 'descripcion': 'Control de malezas con herbicida'},
    {'codigo': '4164', 'descripcion': 'Cosecha manual de caña'},
    {'codigo': '4165', 'descripcion': 'Riego por aspersión'},
    {'codigo': '4166', 'descripcion': 'Poda y limpieza de cultivo'},
    {'codigo': '4167', 'descripcion': 'Aplicación de fungicida'},
    {'codigo': '4168', 'descripcion': 'Trasplante de plántulas'},
    {'codigo': '4169', 'descripcion': 'Mantenimiento de maquinaria'},
    {'codigo': '4170', 'descripcion': 'Transporte de insumos'},
]

cuentas = [
    {'codigo': '522104100091', 'descripcion': 'Insumos agrícolas', 'tipo': 'Gasto'},
    {'codigo': '522104100092', 'descripcion': 'Combustible y lubricantes', 'tipo': 'Gasto'},
    {'codigo': '522104100093', 'descripcion': 'Repuestos de maquinaria', 'tipo': 'Gasto'},
    {'codigo': '522104100094', 'descripcion': 'Servicios de mantenimiento', 'tipo': 'Gasto'},
    {'codigo': '522104100095', 'descripcion': 'Transporte y flete', 'tipo': 'Gasto'},
    {'codigo': '522104100096', 'descripcion': 'Honorarios técnicos', 'tipo': 'Gasto'},
    {'codigo': '522104100097', 'descripcion': 'Herramientas y utensilios', 'tipo': 'Gasto'},
    {'codigo': '522104100098', 'descripcion': 'Gastos administrativos', 'tipo': 'Gasto'},
    {'codigo': '522104100099', 'descripcion': 'Material de oficina', 'tipo': 'Gasto'},
    {'codigo': '522104100100', 'descripcion': 'Seguros de equipos', 'tipo': 'Gasto'},
]

unidades_medida = [
    {'codigo': '14', 'descripcion': 'Litros'},
    {'codigo': '15', 'descripcion': 'Kilogramos'},
    {'codigo': '16', 'descripcion': 'Metros'},
    {'codigo': '17', 'descripcion': 'Unidades'},
    {'codigo': '18', 'descripcion': 'Horas'},
]

variedades = [
    {'codigo': '2', 'descripcion': 'CG02-11400'},
    {'codigo': '3', 'descripcion': 'CG04-11995'},
    {'codigo': '4', 'descripcion': 'G-55'},
    {'codigo': '5', 'descripcion': 'Híbrido 214'},
    {'codigo': '6', 'descripcion': 'Variedad Maya'},
    {'codigo': '7', 'descripcion': 'Caña Dorada'},
    {'codigo': '8', 'descripcion': 'Rubí Tardío'},
    {'codigo': '9', 'descripcion': 'Industria 3030'},
]

tipos_maquina = [
    {'codigo': '2', 'descripcion': 'COSECHADORA'},
    {'codigo': '3', 'descripcion': 'SEMILLADORA'},
    {'codigo': '4', 'descripcion': 'ARADO'},
    {'codigo': '5', 'descripcion': 'MOTONIVELADORA'},
    {'codigo': '6', 'descripcion': 'RETROEXCAVADORA'},
    {'codigo': '7', 'descripcion': 'FUMIGADORA'},
]

marcas = [
    {'codigo': '2', 'descripcion': 'CASE IH'},
    {'codigo': '3', 'descripcion': 'MASSEY FERGUSON'},
    {'codigo': '4', 'descripcion': 'CLAAS'},
    {'codigo': '5', 'descripcion': 'NEW HOLLAND'},
    {'codigo': '6', 'descripcion': 'CATERPILLAR'},
    {'codigo': '7', 'descripcion': 'KUHN'},
    {'codigo': '8', 'descripcion': 'VOLVO'},
    {'codigo': '9', 'descripcion': 'TITAN'},
]

auxiliares = [
    {'codigo': '273', 'nombre': 'San Antonio', 'tipo': 'Finca'},
    {'codigo': '274', 'nombre': 'La Esperanza', 'tipo': 'Finca'},
    {'codigo': '275', 'nombre': 'El Porvenir', 'tipo': 'Finca'},
    {'codigo': '276', 'nombre': 'Nuevo Horizonte', 'tipo': 'Finca'},
    {'codigo': '277', 'nombre': 'Santa María', 'tipo': 'Finca'},
    {'codigo': '278', 'nombre': 'Buenavista', 'tipo': 'Finca'},
    {'codigo': '279', 'nombre': 'El Progreso', 'tipo': 'Finca'},
    {'codigo': '280', 'nombre': 'Los Pinos', 'tipo': 'Finca'},
    {'codigo': '281', 'nombre': 'La Unión', 'tipo': 'Finca'},
    {'codigo': '282', 'nombre': 'Las Delicias', 'tipo': 'Finca'},
]

print('Insertando proveedores...')
for prov in proveedores:
    Proveedor.objects.update_or_create(codigo=prov['codigo'], defaults=prov)
print('Insertando empleados...')
for emp in empleados:
    Empleado.objects.update_or_create(no_cui=emp['no_cui'], defaults=emp)
print('Insertando maquinaria...')
for maq in maquinaria:
    Maquinaria.objects.update_or_create(codigo_maquina=maq['codigo_maquina'], defaults=maq)

print('Insertando labores...')
for lab in labores:
    Labor.objects.update_or_create(codigo=lab['codigo'], defaults=lab)
print('Insertando cuentas...')
for cta in cuentas:
    Cuenta.objects.update_or_create(codigo=cta['codigo'], defaults=cta)
print('Insertando unidades de medida...')
for u in unidades_medida:
    UnidadMedida.objects.update_or_create(codigo=u['codigo'], defaults=u)
print('Insertando variedades...')
for var in variedades:
    Variedad.objects.update_or_create(codigo=var['codigo'], defaults=var)
print('Insertando tipos de máquina...')
for tipo in tipos_maquina:
    TipoMaquina.objects.update_or_create(codigo=tipo['codigo'], defaults=tipo)
print('Insertando marcas...')
for marca in marcas:
    Marca.objects.update_or_create(codigo=marca['codigo'], defaults=marca)
print('Insertando auxiliares...')
for aux in auxiliares:
    Auxiliar.objects.update_or_create(codigo=aux['codigo'], defaults=aux)

print('Insertando municipios...')
municipios_file = os.path.join(os.path.dirname(__file__), 'municipios_data.json')
with open(municipios_file, encoding='utf-8') as f:
    municipios = json.load(f)
for muni in municipios:
    Municipio.objects.update_or_create(
        codigo=muni['codigo'],
        defaults={
            'nombre': muni['nombre'],
            'departamento': muni['departamento'],
        }
    )

print('Datos insertados correctamente.')
