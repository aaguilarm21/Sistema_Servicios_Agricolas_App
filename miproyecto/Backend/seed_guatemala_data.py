import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuraciones.miproyecto.settings')
import django
django.setup()

from accounts.models import Proveedor, Empleado, Maquinaria, Labor, Cuenta, NombrePuesto, UnidadMedida, Variedad, TipoMaquina, Marca, Auxiliar

nombres_puesto = [
    'Piloto',
    'Mecanico',
    'Chofer',
    'Auxiliar Administrativo',
    'Tractorista',
    'Labores Agricolas',
]

cuentas = [
    {'codigo': '522104100001', 'descripcion': 'Siembras', 'tipo': 'Gasto', 'proceso': 'siembras'},
    {'codigo': '522104100002', 'descripcion': 'Fertilización', 'tipo': 'Gasto', 'proceso': 'fertilizacion'},
    {'codigo': '522104100003', 'descripcion': 'Riego', 'tipo': 'Gasto', 'proceso': 'riego'},
]

proveedores = [
    {'codigo': '47789', 'nit': '4561-2', 'razon_social': 'AgroSuministros del Valle, S.A.', 'nombre_propietario': '+502 5555-0101', 'regimen_tributario': 'General (Sobre Utilidades)', 'tipo_factura': 'Factura Electrónica (FEL)', 'dias_credito': 30},
    {'codigo': '12321', 'nit': '6549-8', 'razon_social': 'TecnoRiego & Servicios', 'nombre_propietario': '+502 5555-0102', 'regimen_tributario': 'General (Opcional Simplificado)', 'tipo_factura': 'Factura Electrónica (FEL)', 'dias_credito': 15},
    {'codigo': '89654', 'nit': '9873-1', 'razon_social': 'HidroCampo Proveedores', 'nombre_propietario': '+502 5555-0103', 'regimen_tributario': 'Pequeño Contribuyente', 'tipo_factura': 'Factura Pequeño Contribuyente (FPEQ)', 'dias_credito': 15},
    {'codigo': '39871', 'nit': '234-5', 'razon_social': 'AgroInsumos Continental', 'nombre_propietario': '+502 5555-0104', 'regimen_tributario': 'General (Sobre Utilidades)', 'tipo_factura': 'Factura Electrónica (FEL)', 'dias_credito': 30},
    {'codigo': '65456', 'nit': '7890-3', 'razon_social': 'Central Agrícola de Proveedores', 'nombre_propietario': '+502 5555-0105', 'regimen_tributario': 'General (Opcional Simplificado)', 'tipo_factura': 'Factura Electrónica (FEL)', 'dias_credito': 30},
]

empleados = [
    {'empresa': 'AgroSuministros del Valle, S.A.', 'empleado': 'Luis Fernando López', 'segundo_apellido': 'Méndez', 'no_cui': '3000101234567', 'puesto': '3090', 'nombre_puesto': 'Tractorista'},
    {'empresa': 'TecnoRiego & Servicios', 'empleado': 'Ana María Pacheco', 'segundo_apellido': 'Villatoro', 'no_cui': '3789723456789', 'puesto': '4125', 'nombre_puesto': 'Labores Agricolas'},
    {'empresa': 'HidroCampo Proveedores', 'empleado': 'Carlos Alberto Ramírez', 'segundo_apellido': 'Cifuentes', 'no_cui': '3620149876543', 'puesto': '4150', 'nombre_puesto': 'Chofer'},
    {'empresa': 'AgroInsumos Continental', 'empleado': 'María Elena García', 'segundo_apellido': 'Morales', 'no_cui': '4020158765432', 'puesto': '4210', 'nombre_puesto': 'Auxiliar Administrativo'},
    {'empresa': 'Central Agrícola de Proveedores', 'empleado': 'Jorge Andrés Mendoza', 'segundo_apellido': 'Chávez', 'no_cui': '3020145678901', 'puesto': '3300', 'nombre_puesto': 'Mecanico'},
    {'empresa': 'AgroSuministros del Valle, S.A.', 'empleado': 'Jessica Lorena Castillo', 'segundo_apellido': 'Fuentes', 'no_cui': '2998743210567', 'puesto': '3275', 'nombre_puesto': 'Auxiliar Administrativo'},
    {'empresa': 'TecnoRiego & Servicios', 'empleado': 'Ricardo Estuardo Vásquez', 'segundo_apellido': 'Escobar', 'no_cui': '3321987654321', 'puesto': '4180', 'nombre_puesto': 'Piloto'},
    {'empresa': 'HidroCampo Proveedores', 'empleado': 'Claudia Patricia Solís', 'segundo_apellido': 'Roldán', 'no_cui': '3885601234790', 'puesto': '4300', 'nombre_puesto': 'Auxiliar Administrativo'},
    {'empresa': 'AgroInsumos Continental', 'empleado': 'Fernando José Torres', 'segundo_apellido': 'Maldonado', 'no_cui': '3200987123456', 'puesto': '3400', 'nombre_puesto': 'Mecanico'},
    {'empresa': 'Central Agrícola de Proveedores', 'empleado': 'Yasmin Alejandra Ortiz', 'segundo_apellido': 'Carrillo', 'no_cui': '3165478901234', 'puesto': '4500', 'nombre_puesto': 'Auxiliar Administrativo'},
    {'empresa': 'AgroSuministros del Valle, S.A.', 'empleado': 'Édgar Manuel López', 'segundo_apellido': 'Rosales', 'no_cui': '3147859021345', 'puesto': '4310', 'nombre_puesto': 'Tractorista'},
    {'empresa': 'TecnoRiego & Servicios', 'empleado': 'Sandra Patricia Hernández', 'segundo_apellido': 'Zamora', 'no_cui': '3765890123456', 'puesto': '4400', 'nombre_puesto': 'Auxiliar Administrativo'},
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
    {'codigo': '4161', 'descripcion': 'Siembra de maíz en surcos', 'proceso': 'siembras'},
    {'codigo': '4162', 'descripcion': 'Aplicación de fertilizante foliar', 'proceso': 'fertilizacion'},
    {'codigo': '4165', 'descripcion': 'Riego por aspersión', 'proceso': 'riego'},
    {'codigo': '4168', 'descripcion': 'Trasplante de plántulas', 'proceso': 'siembras'},
    {'codigo': '4169', 'descripcion': 'Preparación de semillero', 'proceso': 'siembras'},
    {'codigo': '4170', 'descripcion': 'Siembra directa', 'proceso': 'siembras'},
    {'codigo': '4171', 'descripcion': 'Resiembra de cultivo', 'proceso': 'siembras'},
    {'codigo': '4172', 'descripcion': 'Aplicación de fertilizante al suelo', 'proceso': 'fertilizacion'},
    {'codigo': '4173', 'descripcion': 'Aplicación de abono orgánico', 'proceso': 'fertilizacion'},
    {'codigo': '4174', 'descripcion': 'Aplicación de fertilizante granulado', 'proceso': 'fertilizacion'},
    {'codigo': '4175', 'descripcion': 'Fertirriego', 'proceso': 'fertilizacion'},
    {'codigo': '4176', 'descripcion': 'Riego por goteo', 'proceso': 'riego'},
    {'codigo': '4177', 'descripcion': 'Riego por gravedad', 'proceso': 'riego'},
    {'codigo': '4178', 'descripcion': 'Riego de establecimiento', 'proceso': 'riego'},
    {'codigo': '4179', 'descripcion': 'Mantenimiento del sistema de riego', 'proceso': 'riego'},
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

print('Insertando nombres de puesto...')
for nombre in nombres_puesto:
    NombrePuesto.objects.get_or_create(nombre=nombre)

print('Insertando cuentas por proceso...')
for cuenta in cuentas:
    Cuenta.objects.update_or_create(proceso=cuenta['proceso'], defaults=cuenta)

print('Insertando labores...')
for lab in labores:
    Labor.objects.update_or_create(codigo=lab['codigo'], defaults=lab)
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

print('Datos insertados correctamente.')
