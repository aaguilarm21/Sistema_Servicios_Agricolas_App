import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# Colores corporativos del sistema agrícola
COLOR_PRIMARY_HEX = "1B5E20"     # Verde oscuro agrícola
COLOR_SECONDARY_HEX = "2E7D32"   # Verde medio
COLOR_ACCENT_HEX = "388E3C"      # Verde vibrante
COLOR_LIGHT_HEX = "E8F5E9"       # Verde muy claro (fondos)
COLOR_DARK_TEXT_HEX = "212121"   # Gris muy oscuro
COLOR_MUTED_HEX = "546E7A"       # Azul pizarra suave
COLOR_WARNING_HEX = "F57F17"     # Ámbar agrícola

COLOR_PRIMARY = RGBColor(0x1B, 0x5E, 0x20)
COLOR_SECONDARY = RGBColor(0x2E, 0x7D, 0x32)
COLOR_DARK = RGBColor(0x21, 0x21, 0x21)
COLOR_MUTED = RGBColor(0x54, 0x6E, 0x7A)

OUTPUT_DIR = os.path.abspath(os.path.dirname(__file__))
IMG_DIR = os.path.join(OUTPUT_DIR, "docs_assets")
os.makedirs(IMG_DIR, exist_ok=True)


def set_cell_background(cell, hex_color):
    """Establece color de fondo de una celda XML en docx."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Establece padding interno de la celda (en dxa: 20 dxa = 1 pt)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def set_table_borders(table, color="B0BEC5", sz="4", val="single"):
    """Aplica bordes finos elegantes a una tabla."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


# ==============================================================================
# GENERACIÓN DE DIAGRAMAS CON MATPLOTLIB (12 DIAGRAMAS)
# ==============================================================================

# --- 1. CRONOGRAMA DE GANTT ---
def generar_diagrama_gantt():
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
    tasks = [
        ("Fase 1: Levantamiento de Requerimientos y Análisis", 1, 4, "#2E7D32"),
        ("Fase 2: Arquitectura y Modelado de Base de Datos", 3, 4, "#388E3C"),
        ("Fase 3: Prototipado y Diseño de Interfaces UX/UI", 5, 3, "#4CAF50"),
        ("Fase 4: Desarrollo Backend y Frontend (Django MVT)", 7, 7, "#1B5E20"),
        ("Fase 5: Módulo de Combustibles y Tanques", 9, 4, "#00796B"),
        ("Fase 6: Módulo de Mantenimiento y Horómetros", 11, 4, "#00897B"),
        ("Fase 7: Verificación Funcional y Pruebas Integrales", 13, 3, "#E65100"),
        ("Fase 8: Despliegue en Servidor y Migración Catálogos", 15, 2, "#F57F17"),
        ("Fase 9: Capacitación a Operadores y Soporte Inicial", 16, 2, "#5D4037"),
        ("Fase 10: Soporte Continuo y Mantenimiento Evolutivo", 17, 4, "#455A64")
    ]
    y_pos = range(len(tasks))
    ax.invert_yaxis()
    for idx, (task, start, duration, color) in enumerate(tasks):
        ax.barh(idx, duration, left=start, height=0.55, align='center', color=color, edgecolor='#212121', linewidth=0.8, alpha=0.9)
        ax.text(start + duration / 2, idx, f"{duration} sem", ha='center', va='center', color='white', fontweight='bold', fontsize=8.5)
        
    ax.set_yticks(y_pos)
    ax.set_yticklabels([t[0] for t in tasks], fontsize=9, fontweight='medium')
    ax.set_xlabel('Semanas del Proyecto (Duración Total: 20 Semanas / 5 Meses)', fontsize=10, fontweight='bold', labelpad=10)
    ax.set_title('CRONOGRAMA GENERAL DE DESARROLLO - SISTEMA DE SERVICIOS AGRÍCOLAS', fontsize=12, fontweight='bold', pad=15, color='#1B5E20')
    ax.set_xlim(0, 21)
    ax.set_xticks(range(1, 22))
    ax.grid(axis='x', linestyle='--', alpha=0.5, color='#90A4AE')
    ax.axvline(x=7, color='#D32F2F', linestyle=':', linewidth=1.5)
    ax.text(7.1, 0, 'Hito 1: Aprobación Diseño', color='#B71C1C', fontsize=7.5, fontweight='bold')
    ax.axvline(x=15, color='#D32F2F', linestyle=':', linewidth=1.5)
    ax.text(15.1, 4, 'Hito 2: Pruebas Piloto', color='#B71C1C', fontsize=7.5, fontweight='bold')
    ax.axvline(x=17, color='#D32F2F', linestyle=':', linewidth=1.5)
    ax.text(17.1, 7, 'Hito 3: Puesta en Producción', color='#B71C1C', fontsize=7.5, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(IMG_DIR, "gantt_chart.png")
    plt.savefig(path, dpi=300)
    plt.close()
    return path


# --- 2. DIAGRAMA DE ARQUITECTURA CLIENTE-SERVIDOR (CAPAS MVT) ---
def generar_diagrama_arquitectura():
    fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Capa 1: Presentación / Cliente
    c1 = patches.FancyBboxPatch((4, 68), 92, 28, boxstyle="round,pad=0.5", fc="#E8F5E9", ec="#2E7D32", lw=1.5)
    ax.add_patch(c1)
    ax.text(6, 92, "CAPA DE PRESENTACIÓN / CLIENTE (FRONTEND WEB & MÓVIL)", fontsize=9.5, fontweight='bold', color='#1B5E20')
    
    # Sub-cajas en cliente
    c_sub1 = patches.FancyBboxPatch((7, 71), 26, 17, boxstyle="round,pad=0.3", fc="#FFFFFF", ec="#81C784", lw=1.2)
    ax.add_patch(c_sub1)
    ax.text(20, 83, "Dispositivos de Campo", ha='center', fontweight='bold', fontsize=8.5, color='#1B5E20')
    ax.text(20, 77, "Smartphones / Tablets\nNavegador Web (Chrome/Safari)\nCaptura de GPS nativa", ha='center', fontsize=7.5, color='#424242')
    
    c_sub2 = patches.FancyBboxPatch((37, 71), 26, 17, boxstyle="round,pad=0.3", fc="#FFFFFF", ec="#81C784", lw=1.2)
    ax.add_patch(c_sub2)
    ax.text(50, 83, "Estaciones Administrativas", ha='center', fontweight='bold', fontsize=8.5, color='#1B5E20')
    ax.text(50, 77, "PC de Escritorio / Laptops\nGestión de Catálogos y Taller\nReportes Consolidados", ha='center', fontsize=7.5, color='#424242')

    c_sub3 = patches.FancyBboxPatch((67, 71), 26, 17, boxstyle="round,pad=0.3", fc="#FFFFFF", ec="#81C784", lw=1.2)
    ax.add_patch(c_sub3)
    ax.text(80, 83, "Capa Interactiva UI", ha='center', fontweight='bold', fontsize=8.5, color='#1B5E20')
    ax.text(80, 77, "HTML5 Semántico + CSS3\nVanilla JS (Sin sobrecargas)\nSistema Toast Notificaciones", ha='center', fontsize=7.5, color='#424242')

    # Flecha Cliente <-> Servidor
    ax.annotate("", xy=(50, 62), xytext=(50, 68), arrowprops=dict(arrowstyle="<->", color="#1565C0", lw=2))
    ax.text(52, 65, "Peticiones HTTP/HTTPS (REST / Form-Data / JSON / AJAX)", color="#1565C0", fontsize=8, fontweight='bold')

    # Capa 2: Lógica de Servidor (Django Backend)
    c2 = patches.FancyBboxPatch((4, 32), 92, 28, boxstyle="round,pad=0.5", fc="#E3F2FD", ec="#1565C0", lw=1.5)
    ax.add_patch(c2)
    ax.text(6, 56, "CAPA DE LÓGICA DE NEGOCIO Y CONTROL (BACKEND DJANGO MVT)", fontsize=9.5, fontweight='bold', color='#0D47A1')

    b_sub1 = patches.FancyBboxPatch((7, 35), 26, 17, boxstyle="round,pad=0.3", fc="#FFFFFF", ec="#90CAF9", lw=1.2)
    ax.add_patch(b_sub1)
    ax.text(20, 47, "Enrutador & Seguridad", ha='center', fontweight='bold', fontsize=8.5, color='#0D47A1')
    ax.text(20, 41, "urls.py (URL Routing)\nMiddleware CSRF & Auth\nAuditoría LoginAttempt", ha='center', fontsize=7.5, color='#424242')

    b_sub2 = patches.FancyBboxPatch((37, 35), 26, 17, boxstyle="round,pad=0.3", fc="#FFFFFF", ec="#90CAF9", lw=1.2)
    ax.add_patch(b_sub2)
    ax.text(50, 47, "Controladores / Vistas", ha='center', fontweight='bold', fontsize=8.5, color='#0D47A1')
    ax.text(50, 41, "views.py (Lógica Operativa)\nDespacho Combustibles\nMantenimiento & Horómetros", ha='center', fontsize=7.5, color='#424242')

    b_sub3 = patches.FancyBboxPatch((67, 35), 26, 17, boxstyle="round,pad=0.3", fc="#FFFFFF", ec="#90CAF9", lw=1.2)
    ax.add_patch(b_sub3)
    ax.text(80, 47, "Capa de Normalización", ha='center', fontweight='bold', fontsize=8.5, color='#0D47A1')
    ax.text(80, 41, "ModeloTextoNormalizado\nEstandarización de textos\nPreservación siglas SAT/CUI", ha='center', fontsize=7.5, color='#424242')

    # Flecha Servidor <-> Datos
    ax.annotate("", xy=(50, 26), xytext=(50, 32), arrowprops=dict(arrowstyle="<->", color="#00796B", lw=2))
    ax.text(52, 29, "Django ORM / Conexión SQL Transaccional ACID", color="#00796B", fontsize=8, fontweight='bold')

    # Capa 3: Persistencia y Datos
    c3 = patches.FancyBboxPatch((4, 4), 92, 20, boxstyle="round,pad=0.5", fc="#FFF3E0", ec="#E65100", lw=1.5)
    ax.add_patch(c3)
    ax.text(6, 20, "CAPA DE PERSISTENCIA Y ALMACENAMIENTO DE DATOS", fontsize=9.5, fontweight='bold', color='#BF360C')

    d_sub1 = patches.FancyBboxPatch((7, 6), 40, 11, boxstyle="round,pad=0.3", fc="#FFFFFF", ec="#FFB74D", lw=1.2)
    ax.add_patch(d_sub1)
    ax.text(27, 13, "Base de Datos Relacional", ha='center', fontweight='bold', fontsize=8.5, color='#BF360C')
    ax.text(27, 8.5, "PostgreSQL (Producción) / SQLite (Desarrollo Local)\nTablas normalizadas en 3FN con integridad referencial", ha='center', fontsize=7.2, color='#424242')

    d_sub2 = patches.FancyBboxPatch((53, 6), 40, 11, boxstyle="round,pad=0.3", fc="#FFFFFF", ec="#FFB74D", lw=1.2)
    ax.add_patch(d_sub2)
    ax.text(73, 13, "Almacenamiento Estático y Archivos", ha='center', fontweight='bold', fontsize=8.5, color='#BF360C')
    ax.text(73, 8.5, "WhiteNoise / StaticFiles (CSS, JS, Iconos corporativos)\nArchivos de auditoría y copias de seguridad automáticas", ha='center', fontsize=7.2, color='#424242')

    ax.set_title("DIAGRAMA DE ARQUITECTURA CLIENTE-SERVIDOR (CAPAS MVT)", fontsize=12, fontweight='bold', color='#1B5E20', pad=10)
    plt.tight_layout()
    path = os.path.join(IMG_DIR, "arquitectura.png")
    plt.savefig(path, dpi=300)
    plt.close()
    return path


# --- 3. DIAGRAMA DE DESPLIEGUE UML (DEPLOYMENT DIAGRAM) ---
def generar_diagrama_despliegue():
    fig, ax = plt.subplots(figsize=(11, 6.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Nodo 1: Dispositivos de Cliente (Nodos 3D)
    n1 = patches.FancyBboxPatch((6, 52), 26, 38, boxstyle="round,pad=0.3", fc="#ECEFF1", ec="#37474F", lw=1.5)
    ax.add_patch(n1)
    ax.text(19, 86, "<<device>>\nDispositivo Cliente\n(Móvil / Tablet / PC)", ha='center', fontweight='bold', fontsize=8.5, color='#263238')
    art1 = patches.Rectangle((8, 55), 22, 22, fc="#FFFFFF", ec="#78909C", lw=1.2)
    ax.add_patch(art1)
    ax.text(19, 71, "<<artifact>>\nNavegador Web\nHTML5 / CSS3\nVanilla JS Client\nGeolocation API", ha='center', fontsize=7.5, color='#37474F')

    # Nodo 2: Servidor Web / Proxy Inverso
    n2 = patches.FancyBboxPatch((38, 52), 26, 38, boxstyle="round,pad=0.3", fc="#E8F5E9", ec="#2E7D32", lw=1.5)
    ax.add_patch(n2)
    ax.text(51, 86, "<<device>>\nServidor Cloud Linux\n(Hosting / Render)", ha='center', fontweight='bold', fontsize=8.5, color='#1B5E20')
    art2 = patches.Rectangle((40, 55), 22, 22, fc="#FFFFFF", ec="#81C784", lw=1.2)
    ax.add_patch(art2)
    ax.text(51, 71, "<<artifact>>\nWSGI Gunicorn\n+ WhiteNoise\nTerminación TLS/SSL\nCompresión Gzip", ha='center', fontsize=7.5, color='#1B5E20')

    # Nodo 3: Contenedor / Aplicación Django
    n3 = patches.FancyBboxPatch((38, 6), 26, 36, boxstyle="round,pad=0.3", fc="#E3F2FD", ec="#1565C0", lw=1.5)
    ax.add_patch(n3)
    ax.text(51, 38, "<<executionEnvironment>>\nPython 3.12 Runtime", ha='center', fontweight='bold', fontsize=8.5, color='#0D47A1')
    art3 = patches.Rectangle((40, 9), 22, 22, fc="#FFFFFF", ec="#90CAF9", lw=1.2)
    ax.add_patch(art3)
    ax.text(51, 23, "<<artifact>>\nDjango 6.0 Engine\nBackend Apps\nAuth & ORM Models\nBusiness Rules", ha='center', fontsize=7.5, color='#0D47A1')

    # Nodo 4: Servidor de Base de Datos
    n4 = patches.FancyBboxPatch((70, 28), 25, 46, boxstyle="round,pad=0.3", fc="#FFF3E0", ec="#E65100", lw=1.5)
    ax.add_patch(n4)
    ax.text(82.5, 70, "<<database>>\nDatabase Server\nPostgreSQL", ha='center', fontweight='bold', fontsize=8.5, color='#BF360C')
    art4 = patches.Rectangle((72, 33), 21, 28, fc="#FFFFFF", ec="#FFB74D", lw=1.2)
    ax.add_patch(art4)
    ax.text(82.5, 51, "<<schema>>\nTablas Agrícolas\n• Maquinaria\n• Combustibles\n• Mantenimiento\n• Registros Campo\n• LoginAttempt", ha='center', fontsize=7.2, color='#BF360C')

    # Conexiones de Despliegue
    # Cliente -> Servidor Web
    ax.plot([32, 38], [71, 71], 'k-', lw=1.8)
    ax.text(35, 74, "HTTPS\n(TLS 1.3)", ha='center', fontsize=7.5, fontweight='bold', color='#1565C0')

    # Servidor Web -> Python Django
    ax.plot([51, 51], [52, 42], 'k-', lw=1.8)
    ax.text(56, 47, "WSGI Socket", ha='center', fontsize=7.5, fontweight='bold', color='#2E7D32')

    # Django -> Base de Datos
    ax.plot([64, 70], [28, 45], 'k-', lw=1.8)
    ax.text(67, 34, "TCP/IP 5432\n(SSL)", ha='center', fontsize=7.2, fontweight='bold', color='#BF360C')

    ax.set_title("DIAGRAMA DE DESPLIEGUE UML (DEPLOYMENT DIAGRAM)", fontsize=12, fontweight='bold', color='#1B5E20', pad=10)
    plt.tight_layout()
    path = os.path.join(IMG_DIR, "despliegue.png")
    plt.savefig(path, dpi=300)
    plt.close()
    return path


# --- 4. DIAGRAMA DE CASOS DE USO UML ---
def generar_diagrama_casos_uso():
    fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    sys_rect = patches.Rectangle((28, 4), 68, 92, fc='#FAFAFA', ec='#37474F', lw=1.5, linestyle='-')
    ax.add_patch(sys_rect)
    ax.text(62, 92, "Sistema de Gestión de Servicios Agrícolas", ha='center', va='center', fontweight='bold', fontsize=11, color='#1B5E20')
    
    actores = [
        {"name": "Administrador\nAgrícola", "x": 12, "y": 80, "color": "#1B5E20"},
        {"name": "Operador /\nCaporal", "x": 12, "y": 55, "color": "#0D47A1"},
        {"name": "Despachador\nde Combustible", "x": 12, "y": 32, "color": "#E65100"},
        {"name": "Mecánico /\nTaller", "x": 12, "y": 12, "color": "#4A148C"}
    ]
    for a in actores:
        circle = patches.Circle((a["x"], a["y"]), 3.2, fc=a["color"], ec='#212121', lw=1.2)
        ax.add_patch(circle)
        ax.text(a["x"], a["y"] - 6.5, a["name"], ha='center', va='top', fontsize=8, fontweight='bold', color='#212121')
        
    use_cases = [
        {"id": "CU1", "name": "Gestionar Usuarios y Roles", "x": 45, "y": 83, "w": 28, "h": 7, "color": "#E8F5E9"},
        {"id": "CU2", "name": "Registrar Boletas Operativas de Campo", "x": 45, "y": 68, "w": 32, "h": 7, "color": "#E3F2FD"},
        {"id": "CU3", "name": "Validar Horómetros y Rendimientos", "x": 75, "y": 68, "w": 19, "h": 7, "color": "#BBDEFB"},
        {"id": "CU4", "name": "Despachar Combustible con Vale", "x": 45, "y": 50, "w": 30, "h": 7, "color": "#FFF3E0"},
        {"id": "CU5", "name": "Actualizar Nivel de Tanques en Vivo", "x": 75, "y": 50, "w": 20, "h": 7, "color": "#FFE0B2"},
        {"id": "CU6", "name": "Registrar Orden de Mantenimiento", "x": 45, "y": 32, "w": 30, "h": 7, "color": "#F3E5F5"},
        {"id": "CU7", "name": "Monitorear Alertas de Horómetro", "x": 45, "y": 18, "w": 30, "h": 7, "color": "#EDE7F6"},
        {"id": "CU8", "name": "Consultar Reportes y Auditoría", "x": 45, "y": 7, "w": 28, "h": 6.5, "color": "#ECEFF1"}
    ]
    for uc in use_cases:
        ellipse = patches.Ellipse((uc["x"] + uc["w"]/2, uc["y"]), uc["w"], uc["h"], fc=uc["color"], ec='#37474F', lw=1.1)
        ax.add_patch(ellipse)
        ax.text(uc["x"] + uc["w"]/2, uc["y"], uc["name"], ha='center', va='center', fontsize=7.5, fontweight='bold', color='#212121')
        
    ax.plot([15, 45], [80, 83], 'k-', lw=1)
    ax.plot([15, 45], [80, 7], 'k-', lw=1)
    ax.plot([15, 45], [55, 68], 'k-', lw=1)
    ax.plot([15, 45], [32, 50], 'k-', lw=1)
    ax.plot([15, 45], [12, 32], 'k-', lw=1)
    ax.plot([15, 45], [12, 18], 'k-', lw=1)
    
    ax.annotate("", xy=(75, 68), xytext=(61, 68), arrowprops=dict(arrowstyle="->", color="#1565C0", lw=1.2, ls="--"))
    ax.text(67, 71, "<<include>>", color="#1565C0", fontsize=6.8, ha='center', fontweight='bold')
    
    ax.annotate("", xy=(75, 50), xytext=(60, 50), arrowprops=dict(arrowstyle="->", color="#E65100", lw=1.2, ls="--"))
    ax.text(67, 53, "<<include>>", color="#E65100", fontsize=6.8, ha='center', fontweight='bold')

    ax.set_title("DIAGRAMA DE CASOS DE USO UML - ACTORES Y LÍMITES DEL SISTEMA", fontsize=12, fontweight='bold', color='#1B5E20', pad=10)
    plt.tight_layout()
    path = os.path.join(IMG_DIR, "casos_uso.png")
    plt.savefig(path, dpi=300)
    plt.close()
    return path


# --- 5. DIAGRAMA DE CLASES UML (ORIENTADO A OBJETOS Y HERENCIA) ---
def generar_diagrama_clases():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Clase Abstracta Base en la parte superior central
    b_class = patches.FancyBboxPatch((32, 75), 36, 21, boxstyle="square,pad=0", fc="#E8F5E9", ec="#2E7D32", lw=1.5)
    ax.add_patch(b_class)
    ax.text(50, 93, "<<Abstract>>\nModeloTextoNormalizado", ha='center', fontweight='bold', fontsize=8.5, color='#1B5E20')
    ax.plot([32, 68], [88, 88], 'k-', lw=0.8)
    ax.text(34, 85, "+ CAMPOS_IDENTIFICACION: frozenset\n+ created_at: DateTimeField\n+ updated_at: DateTimeField", fontsize=7, color='#212121')
    ax.plot([32, 68], [80, 80], 'k-', lw=0.8)
    ax.text(34, 76.5, "+ save(*args, **kwargs): void\n+ normalizar_texto(valor: str): str", fontsize=7, fontweight='bold', color='#1B5E20')

    # Clases Derivadas
    classes = [
        {"name": "Maquinaria", "x": 4, "y": 42, "w": 28, "h": 24, "attrs": ["+ codigo_maquina: CharField [PK]\n+ tipo_maquina: CharField\n+ marca_maquina: CharField\n+ placa_matricula: CharField\n+ combustible: CharField"], "methods": ["+ __str__(): str"], "color": "#E3F2FD", "head": "#1565C0"},
        {"name": "DespachoCombustible", "x": 36, "y": 42, "w": 28, "h": 24, "attrs": ["+ no_vale: CharField [PK]\n+ fecha: DateField\n+ codigo_maquina: CharField [FK]\n+ galones: DecimalField\n+ horometro_actual: DecimalField"], "methods": ["+ calcular_saldo_tanque(): void\n+ __str__(): str"], "color": "#FFF3E0", "head": "#E65100"},
        {"name": "OrdenMantenimiento", "x": 68, "y": 42, "w": 28, "h": 24, "attrs": ["+ codigo_orden: CharField [PK]\n+ codigo_maquina: CharField [FK]\n+ tipo_mantenimiento: CharField\n+ estado: CharField\n+ horometro: DecimalField"], "methods": ["+ cerrar_orden(): void\n+ __str__(): str"], "color": "#F3E5F5", "head": "#6A1B9A"},
        
        {"name": "RegistroOperativo", "x": 4, "y": 8, "w": 28, "h": 24, "attrs": ["+ no_boleta: CharField [PK]\n+ fecha_labor: DateField\n+ finca / lote: CharField\n+ horometro_inicial: DecimalField\n+ horometro_final: DecimalField"], "methods": ["+ calcular_horas(): Decimal\n+ __str__(): str"], "color": "#E8F5E9", "head": "#2E7D32"},
        {"name": "TanqueCombustible", "x": 36, "y": 8, "w": 28, "h": 24, "attrs": ["+ codigo: CharField [PK]\n+ capacidad_galones: DecimalField\n+ nivel_actual_galones: DecimalField\n+ estado: CharField"], "methods": ["+ debitar(gal: Decimal): bool\n+ __str__(): str"], "color": "#FFF3E0", "head": "#E65100"},
        {"name": "ControlServicioHorometro", "x": 68, "y": 8, "w": 28, "h": 24, "attrs": ["+ codigo_maquina: CharField [FK]\n+ intervalo_horas: IntegerField\n+ proximo_horometro: DecimalField\n+ estado_alerta: CharField"], "methods": ["+ actualizar_alerta(): str\n+ __str__(): str"], "color": "#F3E5F5", "head": "#6A1B9A"}
    ]

    for c in classes:
        box = patches.FancyBboxPatch((c["x"], c["y"]), c["w"], c["h"], boxstyle="square,pad=0", fc=c["color"], ec=c["head"], lw=1.2)
        ax.add_patch(box)
        ax.text(c["x"] + c["w"]/2, c["y"] + c["h"] - 3, c["name"], ha='center', fontweight='bold', fontsize=8, color=c["head"])
        ax.plot([c["x"], c["x"] + c["w"]], [c["y"] + c["h"] - 5.5, c["y"] + c["h"] - 5.5], 'k-', lw=0.8)
        ax.text(c["x"] + 1, c["y"] + c["h"] - 7, c["attrs"][0], fontsize=6.8, va='top', color='#212121')
        ax.plot([c["x"], c["x"] + c["w"]], [c["y"] + 6, c["y"] + 6], 'k-', lw=0.8)
        ax.text(c["x"] + 1, c["y"] + 4, c["methods"][0], fontsize=6.8, va='top', color=c["head"], fontweight='bold')

    # Flechas de Herencia (Triángulo blanco hacia la clase base)
    for x_orig in [18, 50, 82]:
        ax.plot([x_orig, x_orig], [66, 72], 'k-', lw=1.2)
        ax.plot([x_orig, 50], [72, 72], 'k-', lw=1.2)
    # Triángulo en base
    ax.annotate("", xy=(50, 75), xytext=(50, 72), arrowprops=dict(arrowstyle="-|>", color="#2E7D32", lw=1.5, mutation_scale=15))

    ax.set_title("DIAGRAMA DE CLASES UML - JERARQUÍA DE HERENCIA Y MÉTODOS DEL MODELO", fontsize=12, fontweight='bold', color='#1B5E20', pad=10)
    plt.tight_layout()
    path = os.path.join(IMG_DIR, "clases.png")
    plt.savefig(path, dpi=300)
    plt.close()
    return path


# --- 6. DIAGRAMA ENTIDAD-RELACIÓN (DER) ---
def generar_diagrama_der():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    entities = [
        {"name": "UserProfile", "x": 5, "y": 70, "w": 26, "h": 24, "pk": "id", "fields": ["usuario_id (FK)", "codigo (UQ)", "puesto", "created_at"], "color": "#E8F5E9", "header": "#2E7D32"},
        {"name": "Maquinaria", "x": 38, "y": 70, "w": 26, "h": 26, "pk": "codigo_maquina (PK)", "fields": ["combustible (S/N)", "tipo_maquina", "marca_maquina", "serie_maquina", "placa_matricula", "id_proveedor"], "color": "#E3F2FD", "header": "#1565C0"},
        {"name": "TanqueCombustible", "x": 72, "y": 70, "w": 25, "h": 24, "pk": "codigo (PK)", "fields": ["nombre", "tipo_combustible", "capacidad_galones", "nivel_actual_galones", "ubicacion", "estado"], "color": "#FFF3E0", "header": "#E65100"},
        
        {"name": "RegistroOperativo", "x": 5, "y": 36, "w": 28, "h": 28, "pk": "id", "fields": ["no_boleta (UQ)", "fecha_labor", "tipo_servicio", "proveedor", "codigo_maquina (FK)", "finca", "lote", "horometro_inicial", "horometro_final", "costo_unitario"], "color": "#E8F5E9", "header": "#2E7D32"},
        {"name": "DespachoCombustible", "x": 38, "y": 36, "w": 28, "h": 28, "pk": "no_vale (PK)", "fields": ["fecha", "codigo_maquina (FK)", "estacion_tanque (FK)", "galones", "horometro_actual", "operador", "labor", "despachado_por"], "color": "#FBE9E7", "header": "#D84315"},
        {"name": "ControlServicioHorometro", "x": 72, "y": 36, "w": 25, "h": 28, "pk": "id", "fields": ["codigo_maquina (FK)", "tipo_servicio", "intervalo_horas", "ultimo_horometro", "proximo_horometro", "horometro_actual", "estado_alerta"], "color": "#F3E5F5", "header": "#6A1B9A"},
        
        {"name": "Empleado", "x": 5, "y": 5, "w": 26, "h": 24, "pk": "id", "fields": ["empresa", "empleado", "no_cui (UQ)", "puesto", "nombre_puesto", "created_at"], "color": "#ECEFF1", "header": "#37474F"},
        {"name": "OrdenMantenimiento", "x": 38, "y": 5, "w": 28, "h": 26, "pk": "codigo_orden (PK)", "fields": ["codigo_maquina (FK)", "fecha_ingreso", "tipo_mantenimiento", "prioridad", "estado", "mecanico", "horometro", "costo_estimado"], "color": "#E0F2F1", "header": "#00695C"},
        {"name": "Proveedor", "x": 72, "y": 5, "w": 25, "h": 24, "pk": "codigo (PK)", "fields": ["nit", "razon_social", "nombre_propietario", "regimen_tributario", "dias_credito"], "color": "#ECEFF1", "header": "#37474F"}
    ]
    for e in entities:
        rect = patches.FancyBboxPatch((e["x"], e["y"]), e["w"], e["h"], boxstyle="round,pad=0.5", fc=e["color"], ec="#37474F", lw=1.2)
        ax.add_patch(rect)
        head_rect = patches.FancyBboxPatch((e["x"], e["y"] + e["h"] - 5), e["w"], 5, boxstyle="square", fc=e["header"], ec="#37474F", lw=1.2)
        ax.add_patch(head_rect)
        ax.text(e["x"] + e["w"] / 2, e["y"] + e["h"] - 2.5, e["name"], ha='center', va='center', color='white', fontweight='bold', fontsize=9.5)
        ax.text(e["x"] + 1, e["y"] + e["h"] - 7.5, f"PK: {e['pk']}", ha='left', va='center', color='#B71C1C', fontweight='bold', fontsize=7.5)
        for f_idx, field in enumerate(e["fields"]):
            ax.text(e["x"] + 1, e["y"] + e["h"] - 10.5 - (f_idx * 2.3), f"• {field}", ha='left', va='center', color='#212121', fontsize=7)
            
    ax.annotate("", xy=(31, 55), xytext=(38, 75), arrowprops=dict(arrowstyle="->", color="#1565C0", lw=1.6, ls="--"))
    ax.text(32, 66, "1:N", color="#1565C0", fontweight='bold', fontsize=8)
    ax.annotate("", xy=(52, 64), xytext=(52, 70), arrowprops=dict(arrowstyle="->", color="#1565C0", lw=1.6, ls="--"))
    ax.text(53, 67, "1:N", color="#1565C0", fontweight='bold', fontsize=8)
    ax.annotate("", xy=(66, 52), xytext=(72, 75), arrowprops=dict(arrowstyle="->", color="#E65100", lw=1.6, ls="--"))
    ax.text(67, 63, "1:N", color="#E65100", fontweight='bold', fontsize=8)
    ax.annotate("", xy=(72, 55), xytext=(64, 75), arrowprops=dict(arrowstyle="->", color="#1565C0", lw=1.6, ls="--"))
    ax.text(66, 68, "1:N", color="#1565C0", fontweight='bold', fontsize=8)
    ax.annotate("", xy=(52, 31), xytext=(52, 36), arrowprops=dict(arrowstyle="->", color="#00695C", lw=1.6, ls="--"))
    ax.text(53, 33, "1:N", color="#00695C", fontweight='bold', fontsize=8)
    
    ax.set_title("DIAGRAMA ENTIDAD-RELACIÓN (DER) - MODELO CONCEPTUAL Y LÓGICO", fontsize=12, fontweight='bold', color='#1B5E20', pad=10)
    plt.tight_layout()
    path = os.path.join(IMG_DIR, "diagrama_der.png")
    plt.savefig(path, dpi=300)
    plt.close()
    return path


# --- 7. DIAGRAMA DE SECUENCIA 1: DESPACHO DE COMBUSTIBLE ---
def generar_diagrama_secuencia():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    participants = [
        {"name": "Despachador\n(Operador)", "x": 15, "color": "#FFE082"},
        {"name": "Interfaz Web\n(Frontend)", "x": 40, "color": "#C8E6C9"},
        {"name": "Servidor Django\n(Backend/Views)", "x": 65, "color": "#BBDEFB"},
        {"name": "Base de Datos\n(PostgreSQL/SQLite)", "x": 90, "color": "#D1C4E9"}
    ]
    for p in participants:
        box = patches.FancyBboxPatch((p["x"] - 9, 88), 18, 9, boxstyle="round,pad=0.2", fc=p["color"], ec='#37474F', lw=1.2)
        ax.add_patch(box)
        ax.text(p["x"], 92.5, p["name"], ha='center', va='center', fontweight='bold', fontsize=8)
        ax.plot([p["x"], p["x"]], [10, 88], 'k--', lw=0.9, alpha=0.7)
        
    steps = [
        (82, 15, 40, "1. Ingresa vale, máquina, galones y horómetro", "->", "#212121"),
        (74, 40, 65, "2. POST /combustibles/despacho/ (Form JSON)", "->", "#1B5E20"),
        (66, 65, 90, "3. SELECT nivel_actual FROM Tanque WHERE codigo=?", "->", "#0D47A1"),
        (58, 90, 65, "4. Retorna nivel disponible", "-->", "#0D47A1"),
        (50, 65, 65, "5. Valida: nivel >= galones y horómetro >= anterior", "loop", "#E65100"),
        (42, 65, 90, "6. INSERT Despacho & UPDATE Tanque & UPDATE Maquina", "->", "#1B5E20"),
        (34, 90, 65, "7. Confirma Commit de Transacción", "-->", "#1B5E20"),
        (26, 65, 40, "8. JSON Response: {status: 'success', no_vale: '...'}", "-->", "#2E7D32"),
        (18, 40, 15, "9. Muestra Notificación Toast Éxito & Imprime Vale", "->", "#2E7D32")
    ]
    for y, x1, x2, text, style, color in steps:
        if style == "loop":
            ax.annotate("", xy=(x1 + 3, y - 4), xytext=(x1, y), arrowprops=dict(arrowstyle="->", color=color, lw=1.2))
            ax.plot([x1, x1 + 5, x1 + 5, x1], [y, y, y - 4, y - 4], color=color, lw=1.2)
            ax.text(x1 + 7, y - 2, text, fontsize=7.2, fontweight='bold', color=color, va='center')
        else:
            ls = "--" if "--" in style else "-"
            ax.annotate("", xy=(x2, y), xytext=(x1, y), arrowprops=dict(arrowstyle="->", color=color, lw=1.2, ls=ls))
            ax.text((x1 + x2)/2, y + 2, text, fontsize=7.2, ha='center', va='bottom', color=color, fontweight='bold')
            
    ax.set_title("DIAGRAMA DE SECUENCIA - TRANSACCIÓN DE DESPACHO DE COMBUSTIBLE", fontsize=11, fontweight='bold', color='#1B5E20', pad=10)
    plt.tight_layout()
    path = os.path.join(IMG_DIR, "secuencia.png")
    plt.savefig(path, dpi=300)
    plt.close()
    return path


# --- 8. DIAGRAMA DE SECUENCIA 2: REGISTRO Y VALIDACIÓN DE BOLETA OPERATIVA ---
def generar_diagrama_secuencia_operativo():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    participants = [
        {"name": "Caporal / Operador\n(Campo)", "x": 15, "color": "#C8E6C9"},
        {"name": "Formulario Boleta\n(Frontend JS)", "x": 40, "color": "#BBDEFB"},
        {"name": "Vistas / Validador\n(Django Backend)", "x": 65, "color": "#FFE082"},
        {"name": "Base de Datos\n(RegistroOperativo)", "x": 90, "color": "#D1C4E9"}
    ]
    for p in participants:
        box = patches.FancyBboxPatch((p["x"] - 9, 88), 18, 9, boxstyle="round,pad=0.2", fc=p["color"], ec='#37474F', lw=1.2)
        ax.add_patch(box)
        ax.text(p["x"], 92.5, p["name"], ha='center', va='center', fontweight='bold', fontsize=8)
        ax.plot([p["x"], p["x"]], [10, 88], 'k--', lw=0.9, alpha=0.7)

    steps = [
        (82, 15, 40, "1. Ingresa boleta, labor, horómetro inicial y final", "->", "#212121"),
        (74, 40, 40, "2. JS calcula: Horas = Final - Inicial (Valida >= 0)", "loop", "#2E7D32"),
        (66, 40, 65, "3. POST /operacion/guardar/ (CSRF + Datos)", "->", "#1565C0"),
        (58, 65, 90, "4. Verifica si existe boleta duplicada", "->", "#0D47A1"),
        (50, 90, 65, "5. Boleta válida (No duplicada)", "-->", "#0D47A1"),
        (42, 65, 65, "6. Normaliza texto y valida labor en proceso", "loop", "#E65100"),
        (34, 65, 90, "7. INSERT RegistroOperativo & UPDATE Horómetro Máquina", "->", "#1B5E20"),
        (26, 65, 40, "8. Retorna HTTP 200 OK {msg: 'Guardado exitoso'}", "-->", "#2E7D32"),
        (18, 40, 15, "9. Notificación Toast Verde + Limpia formulario", "->", "#2E7D32")
    ]
    for y, x1, x2, text, style, color in steps:
        if style == "loop":
            ax.annotate("", xy=(x1 + 3, y - 4), xytext=(x1, y), arrowprops=dict(arrowstyle="->", color=color, lw=1.2))
            ax.plot([x1, x1 + 5, x1 + 5, x1], [y, y, y - 4, y - 4], color=color, lw=1.2)
            ax.text(x1 + 7, y - 2, text, fontsize=7.2, fontweight='bold', color=color, va='center')
        else:
            ls = "--" if "--" in style else "-"
            ax.annotate("", xy=(x2, y), xytext=(x1, y), arrowprops=dict(arrowstyle="->", color=color, lw=1.2, ls=ls))
            ax.text((x1 + x2)/2, y + 2, text, fontsize=7.2, ha='center', va='bottom', color=color, fontweight='bold')

    ax.set_title("DIAGRAMA DE SECUENCIA - CAPTURA Y VALIDACIÓN DE BOLETAS DE CAMPO", fontsize=11, fontweight='bold', color='#1B5E20', pad=10)
    plt.tight_layout()
    path = os.path.join(IMG_DIR, "secuencia_operativo.png")
    plt.savefig(path, dpi=300)
    plt.close()
    return path


# --- 9. DIAGRAMA DE ESTADOS UML (MÁQUINA DE ESTADOS DE FLOTA Y ÓRDENES) ---
def generar_diagrama_estados():
    fig, ax = plt.subplots(figsize=(11, 6.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Sección Superior: Estados de Maquinaria
    ax.text(50, 95, "A. CICLO DE VIDA OPERATIVO DE LA MAQUINARIA AGRÍCOLA", ha='center', fontweight='bold', fontsize=10, color='#1B5E20')
    
    # Inicio Maquinaria
    s_m0 = patches.Circle((8, 80), 2.5, fc='#212121', ec='#212121')
    ax.add_patch(s_m0)
    ax.annotate("", xy=(16, 80), xytext=(10.5, 80), arrowprops=dict(arrowstyle="->", color='#212121', lw=1.2))

    # Estado 1: Disponible
    e1 = patches.FancyBboxPatch((16, 73), 22, 14, boxstyle="round,pad=0.3", fc="#E8F5E9", ec="#2E7D32", lw=1.5)
    ax.add_patch(e1)
    ax.text(27, 82, "Disponible", ha='center', fontweight='bold', fontsize=8.5, color='#1B5E20')
    ax.text(27, 76, "entry / Verificar horómetro\nen patio de maquinaria", ha='center', fontsize=6.8, color='#424242')

    # Estado 2: En Campo
    e2 = patches.FancyBboxPatch((48, 73), 22, 14, boxstyle="round,pad=0.3", fc="#E3F2FD", ec="#1565C0", lw=1.5)
    ax.add_patch(e2)
    ax.text(59, 82, "En Campo", ha='center', fontweight='bold', fontsize=8.5, color='#0D47A1')
    ax.text(59, 76, "do / Ejecutar labor agrícola\n(Siembra / Riego / Cosecha)", ha='center', fontsize=6.8, color='#424242')

    # Estado 3: En Taller
    e3 = patches.FancyBboxPatch((78, 73), 20, 14, boxstyle="round,pad=0.3", fc="#FFF3E0", ec="#E65100", lw=1.5)
    ax.add_patch(e3)
    ax.text(88, 82, "En Taller", ha='center', fontweight='bold', fontsize=8.5, color='#BF360C')
    ax.text(88, 76, "entry / Abrir Orden Mantenimiento\ndo / Reparar y cambiar aceites", ha='center', fontsize=6.5, color='#424242')

    # Transiciones Maquinaria
    # Disponible -> En Campo
    ax.annotate("", xy=(48, 83), xytext=(38, 83), arrowprops=dict(arrowstyle="->", color='#2E7D32', lw=1.2))
    ax.text(43, 85, "Asignar a Lote", ha='center', fontsize=6.8, fontweight='bold', color='#2E7D32')
    # En Campo -> Disponible
    ax.annotate("", xy=(38, 77), xytext=(48, 77), arrowprops=dict(arrowstyle="->", color='#1565C0', lw=1.2))
    ax.text(43, 74, "Finaliza Labor", ha='center', fontsize=6.8, fontweight='bold', color='#1565C0')
    # En Campo -> En Taller
    ax.annotate("", xy=(78, 80), xytext=(70, 80), arrowprops=dict(arrowstyle="->", color='#E65100', lw=1.2))
    ax.text(74, 82, "Falla / Horómetro vencido", ha='center', fontsize=6.5, fontweight='bold', color='#E65100')
    # En Taller -> Disponible
    ax.plot([88, 88, 27, 27], [73, 63, 63, 73], color='#2E7D32', lw=1.2)
    ax.annotate("", xy=(27, 73), xytext=(27, 68), arrowprops=dict(arrowstyle="->", color='#2E7D32', lw=1.2))
    ax.text(58, 65, "Orden Finalizada y Pruebas Superadas", ha='center', fontsize=7, fontweight='bold', color='#2E7D32')

    # Sección Inferior: Estados de Orden de Mantenimiento
    ax.text(50, 48, "B. MÁQUINA DE ESTADOS DE LA ORDEN DE MANTENIMIENTO", ha='center', fontweight='bold', fontsize=10, color='#6A1B9A')

    # Inicio Orden
    s_o0 = patches.Circle((8, 25), 2.5, fc='#212121', ec='#212121')
    ax.add_patch(s_o0)
    ax.annotate("", xy=(16, 25), xytext=(10.5, 25), arrowprops=dict(arrowstyle="->", color='#212121', lw=1.2))

    o1 = patches.FancyBboxPatch((16, 18), 22, 14, boxstyle="round,pad=0.3", fc="#EDE7F6", ec="#512DA8", lw=1.5)
    ax.add_patch(o1)
    ax.text(27, 27, "Pendiente", ha='center', fontweight='bold', fontsize=8.5, color='#4A148C')
    ax.text(27, 21, "Orden generada\nEn espera de turno", ha='center', fontsize=7, color='#424242')

    o2 = patches.FancyBboxPatch((46, 18), 24, 14, boxstyle="round,pad=0.3", fc="#E0F2F1", ec="#00796B", lw=1.5)
    ax.add_patch(o2)
    ax.text(58, 27, "En Taller (En Proceso)", ha='center', fontweight='bold', fontsize=8.5, color='#004D40')
    ax.text(58, 21, "Mecánico asignado\nRepuestos instalados", ha='center', fontsize=7, color='#424242')

    o3 = patches.FancyBboxPatch((78, 18), 20, 14, boxstyle="round,pad=0.3", fc="#E8F5E9", ec="#2E7D32", lw=1.5)
    ax.add_patch(o3)
    ax.text(88, 27, "Finalizada", ha='center', fontweight='bold', fontsize=8.5, color='#1B5E20')
    ax.text(88, 21, "Prueba superada\nHorómetro reseteado", ha='center', fontsize=7, color='#424242')

    # Transiciones Orden
    ax.annotate("", xy=(46, 25), xytext=(38, 25), arrowprops=dict(arrowstyle="->", color='#512DA8', lw=1.2))
    ax.text(42, 27, "Ingreso a Taller", ha='center', fontsize=6.8, fontweight='bold', color='#512DA8')

    ax.annotate("", xy=(78, 25), xytext=(70, 25), arrowprops=dict(arrowstyle="->", color='#00796B', lw=1.2))
    ax.text(74, 27, "Cerrar Trabajo", ha='center', fontsize=6.8, fontweight='bold', color='#00796B')

    ax.set_title("DIAGRAMA DE ESTADOS UML - MAQUINARIA Y ÓRDENES DE TALLER", fontsize=12, fontweight='bold', color='#1B5E20', pad=10)
    plt.tight_layout()
    path = os.path.join(IMG_DIR, "estados.png")
    plt.savefig(path, dpi=300)
    plt.close()
    return path


# --- 10. DIAGRAMA DE ACTIVIDADES UML: MANTENIMIENTO PREVENTIVO ---
def generar_diagrama_actividades():
    fig, ax = plt.subplots(figsize=(8, 7.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    start_c = patches.Circle((50, 95), 2.5, fc='#212121', ec='#212121')
    ax.add_patch(start_c)
    ax.text(50, 98.5, "Inicio de Jornada", ha='center', fontweight='bold', fontsize=8)
    
    ax.annotate("", xy=(50, 88), xytext=(50, 92.5), arrowprops=dict(arrowstyle="->", color='#212121', lw=1.2))
    b1 = patches.FancyBboxPatch((30, 82), 40, 6, boxstyle="round,pad=0.3", fc='#E8F5E9', ec='#2E7D32', lw=1.2)
    ax.add_patch(b1)
    ax.text(50, 85, "Lectura y Registro de Horómetro Diario", ha='center', va='center', fontsize=7.5, fontweight='bold')
    
    ax.annotate("", xy=(50, 75), xytext=(50, 82), arrowprops=dict(arrowstyle="->", color='#212121', lw=1.2))
    d1 = patches.RegularPolygon((50, 71), numVertices=4, radius=4, fc='#FFF9C4', ec='#FBC02D', lw=1.2)
    ax.add_patch(d1)
    ax.text(50, 71, "¿Horómetro Actual >= \nPróximo Servicio?", ha='center', va='center', fontsize=6.5, fontweight='bold')
    
    ax.annotate("", xy=(80, 71), xytext=(54, 71), arrowprops=dict(arrowstyle="->", color='#2E7D32', lw=1.2))
    ax.text(65, 72.5, "[NO] Máquina al día", color='#2E7D32', fontsize=7, fontweight='bold')
    b_no = patches.FancyBboxPatch((70, 48), 24, 6, boxstyle="round,pad=0.3", fc='#E8F5E9', ec='#2E7D32', lw=1.2)
    ax.add_patch(b_no)
    ax.text(82, 51, "Continuar Operación Normal\nen Finca", ha='center', va='center', fontsize=7, fontweight='bold')
    ax.plot([82, 82], [71, 54], color='#2E7D32', lw=1.2)
    
    ax.annotate("", xy=(50, 60), xytext=(50, 67), arrowprops=dict(arrowstyle="->", color='#C62828', lw=1.2))
    ax.text(51, 63.5, "[SÍ] Servicio Requerido", color='#C62828', fontsize=7, fontweight='bold')
    
    b2 = patches.FancyBboxPatch((28, 54), 44, 6, boxstyle="round,pad=0.3", fc='#FFEBEE', ec='#C62828', lw=1.2)
    ax.add_patch(b2)
    ax.text(50, 57, "Generar Alerta Automática de Semáforo (Rojo/Ámbar)", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#B71C1C')
    
    ax.annotate("", xy=(50, 47), xytext=(50, 54), arrowprops=dict(arrowstyle="->", color='#212121', lw=1.2))
    b3 = patches.FancyBboxPatch((28, 41), 44, 6, boxstyle="round,pad=0.3", fc='#EDE7F6', ec='#512DA8', lw=1.2)
    ax.add_patch(b3)
    ax.text(50, 44, "Emitir Orden de Mantenimiento Preventivo", ha='center', va='center', fontsize=7.5, fontweight='bold')
    
    ax.annotate("", xy=(50, 34), xytext=(50, 41), arrowprops=dict(arrowstyle="->", color='#212121', lw=1.2))
    b4 = patches.FancyBboxPatch((28, 28), 44, 6, boxstyle="round,pad=0.3", fc='#E0F2F1', ec='#00796B', lw=1.2)
    ax.add_patch(b4)
    ax.text(50, 31, "Ingreso a Taller, Asignación de Mecánico y Repuestos", ha='center', va='center', fontsize=7.2, fontweight='bold')
    
    ax.annotate("", xy=(50, 21), xytext=(50, 28), arrowprops=dict(arrowstyle="->", color='#212121', lw=1.2))
    b5 = patches.FancyBboxPatch((28, 15), 44, 6, boxstyle="round,pad=0.3", fc='#FFF3E0', ec='#E65100', lw=1.2)
    ax.add_patch(b5)
    ax.text(50, 18, "Cierre de Orden y Actualización de Horómetro Sugerido", ha='center', va='center', fontsize=7.2, fontweight='bold')
    
    ax.annotate("", xy=(50, 8), xytext=(50, 15), arrowprops=dict(arrowstyle="->", color='#212121', lw=1.2))
    ax.plot([82, 82, 54], [48, 8, 8], color='#2E7D32', lw=1.2)
    
    end_outer = patches.Circle((50, 6), 3, fc='white', ec='#212121', lw=1.5)
    end_inner = patches.Circle((50, 6), 2, fc='#212121', ec='#212121')
    ax.add_patch(end_outer)
    ax.add_patch(end_inner)
    ax.text(50, 1.5, "Fin de Ciclo", ha='center', fontweight='bold', fontsize=8)
    
    ax.set_title("DIAGRAMA DE ACTIVIDADES - CONTROL PREVENTIVO POR HORÓMETRO", fontsize=11, fontweight='bold', color='#1B5E20', pad=10)
    plt.tight_layout()
    path = os.path.join(IMG_DIR, "actividades.png")
    plt.savefig(path, dpi=300)
    plt.close()
    return path


# --- 11. DIAGRAMA DE NAVEGACIÓN Y MAPA DEL SITIO (SITE MAP) ---
def generar_diagrama_navegacion():
    fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Raíz: Login / Signup
    r_box = patches.FancyBboxPatch((40, 86), 20, 10, boxstyle="round,pad=0.3", fc="#E8F5E9", ec="#2E7D32", lw=1.5)
    ax.add_patch(r_box)
    ax.text(50, 92, "Autenticación", ha='center', fontweight='bold', fontsize=8.5, color='#1B5E20')
    ax.text(50, 88, "login.html / signup.html", ha='center', fontsize=7, color='#424242')

    # Nivel 1: Dashboard Principal (Home / Módulos)
    m_box = patches.FancyBboxPatch((38, 66), 24, 12, boxstyle="round,pad=0.3", fc="#1B5E20", ec="#004D40", lw=1.5)
    ax.add_patch(m_box)
    ax.text(50, 74, "DASHBOARD PRINCIPAL", ha='center', fontweight='bold', fontsize=9, color='white')
    ax.text(50, 69, "modulos.html / home.html", ha='center', fontsize=7.5, color='#E8F5E9')

    ax.annotate("", xy=(50, 78), xytext=(50, 86), arrowprops=dict(arrowstyle="->", color='#1B5E20', lw=1.5))

    # 4 Módulos Principales
    mods = [
        {"name": "1. Operaciones Campo", "url": "operacion.html\nregistros_operativos.html\nvalidar_registro.html", "x": 4, "y": 38, "w": 20, "h": 18, "fc": "#E3F2FD", "ec": "#1565C0"},
        {"name": "2. Combustibles", "url": "combustibles_despacho.html\ncombustibles_tanques.html\ncombustibles_consumo.html", "x": 28, "y": 38, "w": 20, "h": 18, "fc": "#FFF3E0", "ec": "#E65100"},
        {"name": "3. Mantenimiento", "url": "mantenimiento_flota.html\nmantenimiento_horometros.html\nmantenimiento_ordenes.html", "x": 52, "y": 38, "w": 20, "h": 18, "fc": "#F3E5F5", "ec": "#6A1B9A"},
        {"name": "4. Administración", "url": "configuracion_catalogos.html\nusuarios.html\nreportes.html", "x": 76, "y": 38, "w": 20, "h": 18, "fc": "#E0F2F1", "ec": "#00796B"}
    ]

    for m in mods:
        box = patches.FancyBboxPatch((m["x"], m["y"]), m["w"], m["h"], boxstyle="round,pad=0.3", fc=m["fc"], ec=m["ec"], lw=1.3)
        ax.add_patch(box)
        ax.text(m["x"] + m["w"]/2, m["y"] + m["h"] - 3.5, m["name"], ha='center', fontweight='bold', fontsize=7.8, color=m["ec"])
        ax.text(m["x"] + m["w"]/2, m["y"] + m["h"] - 10, m["url"], ha='center', fontsize=6.8, color='#37474F')
        # Conexión desde Dashboard
        ax.plot([50, m["x"] + m["w"]/2], [66, 61], color='#37474F', lw=1)
        ax.annotate("", xy=(m["x"] + m["w"]/2, m["y"] + m["h"]), xytext=(m["x"] + m["w"]/2, 61), arrowprops=dict(arrowstyle="->", color=m["ec"], lw=1.2))

    # Nivel Inferior: Componentes y Servicios Compartidos
    c_box = patches.FancyBboxPatch((15, 6), 70, 18, boxstyle="round,pad=0.4", fc="#FAFAFA", ec="#78909C", lw=1.3, linestyle='--')
    ax.add_patch(c_box)
    ax.text(50, 20, "SERVICIOS Y COMPONENTES TRANSVERSALES COMPARTIDOS", ha='center', fontweight='bold', fontsize=8.5, color='#37474F')
    ax.text(50, 13, "• Sistema Toast y Modales de Confirmación (notificaciones.js)\n• Auditoría de Ubicación y GPS (LoginAttempt)\n• Normalización Automática de Textos y Siglas SAT (ModeloTextoNormalizado)", ha='center', fontsize=7.5, color='#455A64')

    for m in mods:
        ax.plot([m["x"] + m["w"]/2, m["x"] + m["w"]/2], [m["y"], 24], color='#90A4AE', lw=0.8, linestyle=':')

    ax.set_title("DIAGRAMA DE NAVEGACIÓN Y ARQUITECTURA DE INFORMACIÓN (SITE MAP)", fontsize=12, fontweight='bold', color='#1B5E20', pad=10)
    plt.tight_layout()
    path = os.path.join(IMG_DIR, "navegacion.png")
    plt.savefig(path, dpi=300)
    plt.close()
    return path


# --- 12. WIREFRAME ESTRUCTURAL DE INTERFACES CLAVE ---
def generar_diagrama_wireframes():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6), dpi=300)
    
    # Wireframe 1: Despacho de Combustible
    ax1.set_xlim(0, 100)
    ax1.set_ylim(0, 100)
    ax1.axis('off')
    
    frame1 = patches.Rectangle((2, 2), 96, 96, fc="#FAFAFA", ec="#37474F", lw=1.5)
    ax1.add_patch(frame1)
    # Header
    ax1.add_patch(patches.Rectangle((2, 88), 96, 10, fc="#1B5E20", ec="#1B5E20"))
    ax1.text(6, 93, "SISTEMA AGRÍCOLA | Despacho de Combustible", color='white', fontweight='bold', fontsize=8)
    
    # Selector de Tanque
    ax1.add_patch(patches.FancyBboxPatch((6, 68), 88, 16, boxstyle="round,pad=0.2", fc="#FFF3E0", ec="#E65100", lw=1.2))
    ax1.text(10, 79, "Tanque Suministrador: [ Tanque Principal #1 - Finca El Prado ]", fontsize=7.5, fontweight='bold', color="#BF360C")
    # Barra de Nivel
    ax1.add_patch(patches.Rectangle((10, 71), 70, 4, fc="#FFE0B2", ec="#E65100"))
    ax1.add_patch(patches.Rectangle((10, 71), 52, 4, fc="#E65100", ec="#E65100"))
    ax1.text(82, 72, "74% (3,700 Gal)", fontsize=7, fontweight='bold', color="#BF360C")

    # Formulario
    form_fields = [
        ("No. Vale / Ticket:", "V-2026-00482 (Automático)", 56),
        ("Código de Máquina:", "[ T-04 ] Tractor John Deere 8245R", 46),
        ("Galones a Suministrar:", "[ 45.00 ] Galones", 36),
        ("Horómetro de Carga:", "[ 3,845.50 ] Horas", 26),
        ("Operador / Conductor:", "[ Juan Pérez - Caporal 01 ]", 16)
    ]
    for lbl, val, y_pos in form_fields:
        ax1.text(8, y_pos + 4, lbl, fontsize=7, fontweight='bold', color="#263238")
        ax1.add_patch(patches.Rectangle((8, y_pos - 3), 84, 6, fc="#FFFFFF", ec="#B0BEC5", lw=1))
        ax1.text(10, y_pos - 1, val, fontsize=6.8, color="#455A64")

    # Botón Guardar
    ax1.add_patch(patches.FancyBboxPatch((54, 5), 38, 6.5, boxstyle="round,pad=0.2", fc="#2E7D32", ec="#1B5E20"))
    ax1.text(73, 8.2, "Registrar Despacho", ha='center', color='white', fontweight='bold', fontsize=7.5)

    ax1.set_title("A. Wireframe: Despacho de Combustible", fontsize=10, fontweight='bold', color='#1B5E20', pad=8)

    # Wireframe 2: Matriz de Control por Horómetro (Semáforo)
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 100)
    ax2.axis('off')

    frame2 = patches.Rectangle((2, 2), 96, 96, fc="#FAFAFA", ec="#37474F", lw=1.5)
    ax2.add_patch(frame2)
    # Header
    ax2.add_patch(patches.Rectangle((2, 88), 96, 10, fc="#1B5E20", ec="#1B5E20"))
    ax2.text(6, 93, "SISTEMA AGRÍCOLA | Control y Semáforo de Horómetros", color='white', fontweight='bold', fontsize=8)

    cards = [
        ("T-01 | John Deere 6110D", "Horómetro Actual: 1,240 hrs\nPróximo Servicio: 1,500 hrs\nMargen: +260 hrs restantes", "AL DÍA", "#E8F5E9", "#2E7D32", 67),
        ("T-04 | Case Puma 210", "Horómetro Actual: 2,485 hrs\nPróximo Servicio: 2,500 hrs\nMargen: ¡Solo 15 hrs restantes!", "PRÓXIMO A VENCER", "#FFF9C4", "#F57F17", 45),
        ("C-02 | Cosechadora Case 8810", "Horómetro Actual: 4,020 hrs\nPróximo Servicio: 4,000 hrs\n¡Excedido por 20 horas de trabajo!", "VENCIDO - ACCIÓN", "#FFEBEE", "#C62828", 23)
    ]

    for title, desc, badge, fc, ec, y_pos in cards:
        card = patches.FancyBboxPatch((6, y_pos), 88, 18, boxstyle="round,pad=0.3", fc=fc, ec=ec, lw=1.3)
        ax2.add_patch(card)
        ax2.text(10, y_pos + 13, title, fontsize=7.5, fontweight='bold', color=ec)
        ax2.text(10, y_pos + 4, desc, fontsize=6.8, color="#37474F")
        # Badge
        ax2.add_patch(patches.FancyBboxPatch((62, y_pos + 9), 30, 6, boxstyle="round,pad=0.2", fc=ec, ec=ec))
        ax2.text(77, y_pos + 12, badge, ha='center', color='white', fontweight='bold', fontsize=6.5)
        # Botón Apertura
        ax2.add_patch(patches.Rectangle((62, y_pos + 2), 30, 5, fc="#FFFFFF", ec=ec, lw=0.9))
        ax2.text(77, y_pos + 4.5, "Crear Orden Taller", ha='center', color=ec, fontweight='bold', fontsize=6.2)

    ax2.set_title("B. Wireframe: Matriz Preventiva de Horómetros", fontsize=10, fontweight='bold', color='#1B5E20', pad=8)

    plt.tight_layout()
    path = os.path.join(IMG_DIR, "wireframes.png")
    plt.savefig(path, dpi=300)
    plt.close()
    return path


# ==============================================================================
# CONSTRUCCIÓN DEL DOCUMENTO WORD (.DOCX) CON 12 DIAGRAMAS
# ==============================================================================

def crear_documento():
    doc = Document()
    
    # Configuración de márgenes estándar
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
        
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = COLOR_DARK
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)
    
    # -------------------------------------------------------------
    # PORTADA ELEGANTE
    # -------------------------------------------------------------
    p_portada_pre = doc.add_paragraph()
    p_portada_pre.paragraph_format.space_before = Pt(36)
    p_portada_pre.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_portada_pre.add_run("ESPECIFICACIÓN COMPLETA DE INGENIERÍA DE SOFTWARE")
    r_sub.font.size = Pt(13)
    r_sub.font.bold = True
    r_sub.font.color.rgb = COLOR_SECONDARY
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(18)
    r_title = p_title.add_run("SISTEMA DE GESTIÓN DE SERVICIOS AGRÍCOLAS, COMBUSTIBLE Y MANTENIMIENTO DE MAQUINARIA")
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_PRIMARY
    
    p_bar = doc.add_paragraph()
    p_bar.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_bar = p_bar.add_run("―" * 38)
    r_bar.font.bold = True
    r_bar.font.color.rgb = COLOR_SECONDARY
    
    p_desc = doc.add_paragraph()
    p_desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_desc.paragraph_format.space_before = Pt(18)
    p_desc.paragraph_format.space_after = Pt(64)
    r_desc = p_desc.add_run(
        "Estudios de Factibilidad, Ciclo de Vida del Software, Cronograma Gantt,\n"
        "Modelado UML Completo (Estructural, Comportamiento y Arquitectura) y Diseño de Interfaces"
    )
    r_desc.font.size = Pt(12)
    r_desc.font.italic = True
    r_desc.font.color.rgb = COLOR_MUTED
    
    # Metadata Box
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Proyecto:", "Sistema Integral de Servicios Agrícolas"),
        ("Tecnologías:", "Python 3 / Django Framework, PostgreSQL/SQLite, HTML5/CSS3/Vanilla JS"),
        ("Ámbito Operativo:", "Sector Agroindustrial (Caña de Azúcar, Siembras, Riego y Maquinaria Pesada)"),
        ("Documentación UML:", "12 Diagramas Formales de Ingeniería (Arquitectura, DER, Gantt, Secuencia, Clases, Estados, Interfaces)")
    ]
    for row_idx, (k, v) in enumerate(meta_data):
        c1, c2 = meta_table.rows[row_idx].cells
        c1.width = Inches(2.2)
        c2.width = Inches(4.3)
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(k)
        r1.bold = True
        r1.font.color.rgb = COLOR_PRIMARY
        p2 = c2.paragraphs[0]
        p2.add_run(v)
        set_cell_background(c1, COLOR_LIGHT_HEX)
        set_cell_background(c2, "F9FBE7")
        set_cell_margins(c1, top=80, bottom=80, left=100, right=100)
        set_cell_margins(c2, top=80, bottom=80, left=100, right=100)
    set_table_borders(meta_table, color="A5D6A7")
    
    doc.add_page_break()
    
    # -------------------------------------------------------------
    # TABLA DE CONTENIDO (RESUMEN ESTRUCTURAL)
    # -------------------------------------------------------------
    h_toc = doc.add_paragraph()
    h_toc.paragraph_format.space_before = Pt(12)
    h_toc.paragraph_format.space_after = Pt(12)
    r_toc = h_toc.add_run("CONTENIDO DEL DOCUMENTO Y CATÁLOGO DE DIAGRAMAS")
    r_toc.font.size = Pt(16)
    r_toc.font.bold = True
    r_toc.font.color.rgb = COLOR_PRIMARY
    
    toc_items = [
        ("e. Estudios de Factibilidad", "Evaluación multidimensional: técnica, operativa, económica, legal y ambiental"),
        ("f. Fases de Desarrollo del Proyecto", "Ingeniería de software: Análisis, Diseño, Pruebas, Implementación y Mantenimiento"),
        ("   • Diagrama 1: Arquitectura Cliente-Servidor MVT", "Capas de Presentación, Lógica Django y Persistencia"),
        ("   • Diagrama 2: Despliegue UML (Deployment Diagram)", "Nodos de clientes móviles, WSGI Gunicorn, Cloud y Base de Datos"),
        ("g. Cronograma de Desarrollo (Diagrama de Gantt)", "Planificación temporal en 20 semanas con hitos críticos de entrega"),
        ("   • Diagrama 3: Diagrama de Gantt del Cronograma", "Gráfico temporal con ruta crítica y 3 hitos de verificación"),
        ("h. Diseño del Sistema UML", "Modelado formal estructural y de comportamiento del sistema"),
        ("   • Diagrama 4: Casos de Uso General del Sistema", "Actores (Administrador, Operador, Despachador, Mecánico)"),
        ("   • Diagrama 5: Clases UML (Orientado a Objetos)", "Estructura de clases, ModeloTextoNormalizado y herencia"),
        ("   • Diagrama 6: Entidad-Relación (DER)", "Estructura relacional de base de datos en Tercera Forma Normal (3FN)"),
        ("   • Diagrama 7: Secuencia - Despacho de Combustible", "Transacción atómica de combustible con validación de tanque"),
        ("   • Diagrama 8: Secuencia - Boletas de Campo", "Captura de horómetros de labor y rendimientos por hectárea"),
        ("   • Diagrama 9: Estados UML (State Machine)", "Ciclo de vida de maquinaria y órdenes de mantenimiento"),
        ("   • Diagrama 10: Actividades - Control por Horómetro", "Flujo de control y decisiones del semáforo preventivo"),
        ("i. Diseño de Interfaces y Experiencia de Usuario", "Catálogo exhaustivo de interfaces, ergonomía y flujos visuales"),
        ("   • Diagrama 11: Navegación del Sistema (Site Map)", "Mapa arquitectónico de pantallas, módulos y componentes"),
        ("   • Diagrama 12: Wireframes de Interfaces Insignia", "Maquetación funcional de Despacho de Diésel y Matriz de Horómetros")
    ]
    
    toc_table = doc.add_table(rows=len(toc_items), cols=2)
    toc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (title, desc) in enumerate(toc_items):
        c1, c2 = toc_table.rows[idx].cells
        c1.width = Inches(3.4)
        c2.width = Inches(3.3)
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(title)
        if not title.startswith("   •"):
            r1.bold = True
            r1.font.color.rgb = COLOR_PRIMARY
            set_cell_background(c1, COLOR_LIGHT_HEX)
            set_cell_background(c2, COLOR_LIGHT_HEX)
        else:
            r1.font.color.rgb = COLOR_DARK
            r1.font.size = Pt(10)
        p2 = c2.paragraphs[0]
        r2 = p2.add_run(desc)
        r2.font.size = Pt(9.5)
        r2.font.italic = True
        set_cell_margins(c1, top=40, bottom=40, left=80, right=80)
        set_cell_margins(c2, top=40, bottom=40, left=80, right=80)
    set_table_borders(toc_table, color="CFD8DC")
    
    doc.add_page_break()
    
    # -------------------------------------------------------------
    # SECCIÓN E: ESTUDIOS DE FACTIBILIDAD
    # -------------------------------------------------------------
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(18)
    h1.paragraph_format.space_after = Pt(8)
    r1 = h1.add_run("e. Estudios de Factibilidad")
    r1.font.size = Pt(18)
    r1.font.bold = True
    r1.font.color.rgb = COLOR_PRIMARY
    
    p = doc.add_paragraph()
    p.add_run(
        "El estudio de factibilidad determina la viabilidad global de la implementación del Sistema de Gestión de Servicios "
        "Agrícolas en el entorno empresarial e industrial. Se evalúan cinco dimensiones: técnica, operativa, económica, "
        "legal y ambiental, demostrando la sostenibilidad y pertinencia del proyecto."
    )
    
    # Factibilidad Técnica
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(6)
    r2 = h2.add_run("Factibilidad Técnica")
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_SECONDARY
    
    bullet_tec = [
        ("Arquitectura y Lenguajes:", "Python con Django 6.0 (patrón MVT), proporcionando un servidor rápido, seguro contra inyecciones SQL y ataques CSRF, y con ORM maduro."),
        ("Bases de Datos:", "PostgreSQL para producción y SQLite para desarrollo y pruebas locales. Ambas garantizan transacciones con propiedades ACID indispensables para el control de inventarios de combustible y horómetros."),
        ("Frontend y Redes Rurales:", "HTML5 semántico, CSS3 y JavaScript moderno nativo (Vanilla JS). Carga instantánea sin dependencias pesadas en conexiones 3G/4G inestables de fincas agrícolas."),
        ("Geolocalización y Auditoría:", "Captura automática de coordenadas GPS (latitud y longitud), dirección IP y agente de usuario en la tabla `LoginAttempt` para trazabilidad de accesos.")
    ]
    for b_title, b_text in bullet_tec:
        bp = doc.add_paragraph(style='List Bullet')
        br_title = bp.add_run(b_title + " ")
        br_title.bold = True
        br_title.font.color.rgb = COLOR_PRIMARY
        bp.add_run(b_text)

    # Factibilidad Operativa
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    r2 = h2.add_run("Factibilidad Operativa")
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_SECONDARY
    
    bullet_op = [
        ("Curva de Aprendizaje:", "Diseño ergonómico e intuitivo con código de colores (verde para al día, amarillo para preventivo y rojo para vencido)."),
        ("Normalización de Datos:", "La clase abstracta `ModeloTextoNormalizado` convierte entradas a formato estandarizado y respeta siglas técnicas guatemaltecas (NIT, CUI, DPI, RTK, GPS, SAT)."),
        ("Flujo Integrado:", "Conexión transparente entre despachadores de combustible, mecánicos de taller, caporales de campo y la gerencia general en una plataforma unificada.")
    ]
    for b_title, b_text in bullet_op:
        bp = doc.add_paragraph(style='List Bullet')
        br_title = bp.add_run(b_title + " ")
        br_title.bold = True
        br_title.font.color.rgb = COLOR_PRIMARY
        bp.add_run(b_text)

    # Factibilidad Económica
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    r2 = h2.add_run("Factibilidad Económica")
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_SECONDARY
    
    econ_table = doc.add_table(rows=7, cols=3)
    econ_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    econ_headers = ["Rubro de Inversión / Ahorro", "Tipo", "Monto Estimado (Quetzales - Q)"]
    for i, h in enumerate(econ_headers):
        cell = econ_table.rows[0].cells[i]
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, COLOR_PRIMARY_HEX)
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        
    econ_rows = [
        ("Desarrollo de Software y Arquitectura (5 meses)", "Inversión Inicial (CAPEX)", "Q 45,000.00"),
        ("Servidor Cloud (Render / Postgres) y Dominio Anual", "Costo Operativo (OPEX)", "Q 3,600.00"),
        ("Capacitación presencial y material para operadores", "Inversión Inicial (CAPEX)", "Q 4,500.00"),
        ("Ahorro por mitigación de mermas y desvío de combustible diésel (5-8%)", "Beneficio Anual", "+ Q 72,000.00"),
        ("Ahorro por prevención de fallas catastróficas en motores (control horómetros)", "Beneficio Anual", "+ Q 48,000.00"),
        ("Optimización de tiempos administrativos y reportería automatizada", "Beneficio Anual", "+ Q 18,000.00")
    ]
    for r_idx, row in enumerate(econ_rows):
        for c_idx, val in enumerate(row):
            cell = econ_table.rows[r_idx + 1].cells[c_idx]
            p = cell.paragraphs[0]
            p.add_run(val)
            if c_idx == 2:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                if val.startswith("+"):
                    p.runs[0].font.color.rgb = COLOR_SECONDARY
                    p.runs[0].bold = True
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            if r_idx % 2 == 1:
                set_cell_background(cell, "F5F5F5")
    set_table_borders(econ_table)
    
    p_roi = doc.add_paragraph()
    p_roi.paragraph_format.space_before = Pt(8)
    r_roi = p_roi.add_run(
        "Conclusión Económica: Inversión inicial de Q 53,100.00 frente a ahorros anuales proyectados de Q 138,000.00. "
        "Retorno de Inversión (ROI) superior al 159% con recuperación de capital en 4.6 meses."
    )
    r_roi.bold = True
    r_roi.font.color.rgb = COLOR_PRIMARY

    # Factibilidad Legal
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    r2 = h2.add_run("Factibilidad Legal")
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_SECONDARY
    
    bullet_leg = [
        ("Tributaria SAT:", "Registro de NIT, régimen fiscal y compatibilidad con Factura Electrónica en Línea (FEL)."),
        ("Laboral RENAP:", "Validación estricta de 13 dígitos numéricos para el CUI/DPI según la legislación de Guatemala."),
        ("Licenciamiento:", "Pila tecnológica en software libre permisivo (Python, Django, PostgreSQL, Linux) sin costos por licencias."),
        ("Protección de Datos:", "Cifrado de credenciales con algoritmos estándar PBKDF2/SHA-256 y control de roles.")
    ]
    for b_title, b_text in bullet_leg:
        bp = doc.add_paragraph(style='List Bullet')
        br_title = bp.add_run(b_title + " ")
        br_title.bold = True
        br_title.font.color.rgb = COLOR_PRIMARY
        bp.add_run(b_text)

    # Factibilidad Ambiental
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    r2 = h2.add_run("Factibilidad Ambiental")
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_SECONDARY
    
    bullet_amb = [
        ("Eficiencia Energética:", "Control de consumo de diésel por horómetro que detecta motores ineficientes y reduce emisiones de CO₂."),
        ("Prevención de Derrames:", "Monitoreo continuo de tanques de abastecimiento para evitar filtraciones en suelos de cultivo."),
        ("Gestión de Residuos:", "Trazabilidad de cambios de lubricantes y filtros según regulaciones ambientales del MARN."),
        ("Cero Papel:", "Digitalización completa de boletas de campo, vales y órdenes de taller.")
    ]
    for b_title, b_text in bullet_amb:
        bp = doc.add_paragraph(style='List Bullet')
        br_title = bp.add_run(b_title + " ")
        br_title.bold = True
        br_title.font.color.rgb = COLOR_PRIMARY
        bp.add_run(b_text)
        
    doc.add_page_break()

    # -------------------------------------------------------------
    # SECCIÓN F: FASES DE DESARROLLO DEL PROYECTO
    # -------------------------------------------------------------
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(18)
    h1.paragraph_format.space_after = Pt(8)
    r1 = h1.add_run("f. Fases de Desarrollo del Proyecto")
    r1.font.size = Pt(18)
    r1.font.bold = True
    r1.font.color.rgb = COLOR_PRIMARY
    
    # Fase de Análisis
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(6)
    r2 = h2.add_run("Fase de Análisis")
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_SECONDARY
    
    p = doc.add_paragraph()
    p.add_run(
        "Levantamiento de requerimientos, identificación de problemáticas y delimitación del alcance. "
        "En esta etapa se estudiaron los procesos agrícolas en fincas, estaciones de combustible y talleres mecánicos."
    )
    
    req_table = doc.add_table(rows=6, cols=3)
    req_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    req_headers = ["Código", "Tipo", "Descripción del Requerimiento"]
    for i, h in enumerate(req_headers):
        cell = req_table.rows[0].cells[i]
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, COLOR_SECONDARY_HEX)
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
        
    req_data = [
        ("RF-01", "Funcional", "Control integral de despacho de combustible con correlativo único de vales y débito automático al tanque."),
        ("RF-02", "Funcional", "Gestión de boletas operativas con cálculo de rendimientos por hectárea, labor y horómetro."),
        ("RF-03", "Funcional", "Sistema de semáforo de alerta preventiva por horómetro de máquina (Al Día, Próximo a Vencer, Vencido)."),
        ("RNF-01", "No Funcional", "Seguridad con protección CSRF, sanitización de entradas y registro de intentos de login con GPS."),
        ("RNF-02", "No Funcional", "Diseño responsivo optimizado para carga rápida en redes móviles de baja cobertura en fincas.")
    ]
    for r_idx, (c, t, d) in enumerate(req_data):
        cell_c, cell_t, cell_d = req_table.rows[r_idx + 1].cells
        cell_c.paragraphs[0].add_run(c).bold = True
        cell_t.paragraphs[0].add_run(t)
        cell_d.paragraphs[0].add_run(d)
        set_cell_margins(cell_c, top=60, bottom=60, left=80, right=80)
        set_cell_margins(cell_t, top=60, bottom=60, left=80, right=80)
        set_cell_margins(cell_d, top=60, bottom=60, left=80, right=80)
        if r_idx % 2 == 1:
            set_cell_background(cell_c, "F9FBE7")
            set_cell_background(cell_t, "F9FBE7")
            set_cell_background(cell_d, "F9FBE7")
    set_table_borders(req_table)

    # Fase de Diseño
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    r2 = h2.add_run("Fase de Diseño y Arquitectura del Sistema")
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_SECONDARY
    
    p = doc.add_paragraph()
    p.add_run(
        "Definición de arquitectura cliente-servidor, modelado de base de datos relacional y prototipado de interfaces. "
        "El sistema se estructura en una arquitectura Modelo-Vista-Template (MVT) modular de tres capas:"
    )
    
    # Diagrama 1: Arquitectura
    arq_path = generar_diagrama_arquitectura()
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(arq_path, width=Inches(6.4))
    p_caption = doc.add_paragraph()
    p_caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap = p_caption.add_run("Figura 1: Diagrama de Arquitectura Cliente-Servidor MVT y Flujo de Datos")
    r_cap.font.size = Pt(9.5)
    r_cap.font.italic = True
    r_cap.font.color.rgb = COLOR_MUTED

    p = doc.add_paragraph()
    p.add_run(
        "Para materializar la arquitectura física y de redes en el entorno de producción, se especifica el "
        "Diagrama de Despliegue UML que define los nodos de hardware, contenedores y protocolos de comunicación:"
    )

    # Diagrama 2: Despliegue
    desp_path = generar_diagrama_despliegue()
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(desp_path, width=Inches(6.4))
    p_caption = doc.add_paragraph()
    p_caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap = p_caption.add_run("Figura 2: Diagrama de Despliegue UML (Deployment Diagram) en Entorno Cloud")
    r_cap.font.size = Pt(9.5)
    r_cap.font.italic = True
    r_cap.font.color.rgb = COLOR_MUTED

    # Fase de Pruebas
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    r2 = h2.add_run("Fase de Pruebas")
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_SECONDARY
    
    bullet_pru = [
        ("Validación de Reglas de Negocio:", "Horómetro final obligatoriamente mayor o igual al horómetro inicial; galones despachados no pueden exceder la existencia del tanque."),
        ("Pruebas de Concurrencia:", "Simulación de múltiples despachos simultáneos para verificar bloqueos atómicos en bases de datos relacionales."),
        ("Seguridad:", "Validación de protección CSRF en todos los formularios POST, sanitización de búsquedas y comprobación de expiración de sesiones."),
        ("Pruebas de Usabilidad en Campo (UAT):", "Verificación práctica con operadores y caporales bajo luz solar directa en teléfonos y tabletas.")
    ]
    for b_title, b_text in bullet_pru:
        bp = doc.add_paragraph(style='List Bullet')
        br_title = bp.add_run(b_title + " ")
        br_title.bold = True
        br_title.font.color.rgb = COLOR_PRIMARY
        bp.add_run(b_text)

    # Fase de Implementación
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    r2 = h2.add_run("Fase de Implementación")
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_SECONDARY
    
    bullet_imp = [
        ("Configuración de Servidores:", "Linux, Gunicorn como servidor WSGI, compresión WhiteNoise y gestión de secretos con `.env`."),
        ("Migración de Catálogos (Seeding):", "Población de municipios guatemaltecos, marcas de maquinaria, labores y cuentas contables."),
        ("Capacitación:", "Talleres prácticos a administradores, mecánicos de taller y despachadores de combustible.")
    ]
    for b_title, b_text in bullet_imp:
        bp = doc.add_paragraph(style='List Bullet')
        br_title = bp.add_run(b_title + " ")
        br_title.bold = True
        br_title.font.color.rgb = COLOR_PRIMARY
        bp.add_run(b_text)

    # Fase de Mantenimiento
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    r2 = h2.add_run("Fase de Mantenimiento")
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_SECONDARY
    
    bullet_man = [
        ("Correctivo:", "Atención inmediata a fallas operativas o discrepancias en saldos."),
        ("Perfectivo:", "Optimización continua de consultas con `select_related` y creación de índices."),
        ("Adaptativo:", "Adecuación ante eventuales reformas en requisitos tributarios de la SAT."),
        ("Respaldos (Backups):", "Copias de seguridad diarias automatizadas hacia almacenamiento redundante.")
    ]
    for b_title, b_text in bullet_man:
        bp = doc.add_paragraph(style='List Bullet')
        br_title = bp.add_run(b_title + " ")
        br_title.bold = True
        br_title.font.color.rgb = COLOR_PRIMARY
        bp.add_run(b_text)
        
    doc.add_page_break()

    # -------------------------------------------------------------
    # SECCIÓN G: CRONOGRAMA DE DESARROLLO (DIAGRAMA DE GANTT)
    # -------------------------------------------------------------
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(18)
    h1.paragraph_format.space_after = Pt(8)
    r1 = h1.add_run("g. Cronograma de Desarrollo (Diagrama de Gantt)")
    r1.font.size = Pt(18)
    r1.font.bold = True
    r1.font.color.rgb = COLOR_PRIMARY
    
    p = doc.add_paragraph()
    p.add_run(
        "El cronograma de desarrollo del proyecto abarca 20 semanas (5 meses de trabajo), organizadas de forma "
        "consecutiva y superpuesta según sus dependencias técnicas. El siguiente diagrama ilustra la programación temporal "
        "y los tres hitos fundamentales del proyecto:"
    )
    
    # Diagrama 3: Gantt
    gantt_path = generar_diagrama_gantt()
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(gantt_path, width=Inches(6.4))
    p_caption = doc.add_paragraph()
    p_caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap = p_caption.add_run("Figura 3: Diagrama de Gantt del Cronograma de Ingeniería del Proyecto (Semanas 1 a 20)")
    r_cap.font.size = Pt(9.5)
    r_cap.font.italic = True
    r_cap.font.color.rgb = COLOR_MUTED
    
    # Tabla WBS
    gantt_tbl = doc.add_table(rows=11, cols=4)
    gantt_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    g_headers = ["Fase del Proyecto", "Duración", "Periodo", "Entregable Principal"]
    for i, h in enumerate(g_headers):
        cell = gantt_tbl.rows[0].cells[i]
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, COLOR_PRIMARY_HEX)
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
        
    g_rows = [
        ("Fase 1: Levantamiento y Análisis", "4 semanas", "Semana 1 - 4", "Documento de Especificación de Requerimientos de Software (SRS)"),
        ("Fase 2: Arquitectura y Base de Datos", "4 semanas", "Semana 3 - 6", "Modelo Entidad-Relación y Esquema Relacional de Base de Datos"),
        ("Fase 3: Prototipado UX/UI", "3 semanas", "Semana 5 - 7", "Wireframes y Plantillas Base HTML5/CSS3 Aprobadas"),
        ("Fase 4: Desarrollo Backend / Frontend", "7 semanas", "Semana 7 - 13", "Núcleo Django MVT, Catálogos y Registros Operativos"),
        ("Fase 5: Módulo Combustibles y Tanques", "4 semanas", "Semana 9 - 12", "Control de Despachos, Vales y Saldos de Tanques"),
        ("Fase 6: Mantenimiento y Horómetros", "4 semanas", "Semana 11 - 14", "Matriz de Semáforos y Órdenes de Mantenimiento"),
        ("Fase 7: Verificación y Pruebas", "3 semanas", "Semana 13 - 15", "Informe de Calidad QA, Seguridad y Validación de Negocio"),
        ("Fase 8: Despliegue en Servidor", "2 semanas", "Semana 15 - 16", "Entorno de Producción Cloud Operativo con Catálogos"),
        ("Fase 9: Capacitación de Usuarios", "2 semanas", "Semana 16 - 17", "Personal de Campo y Administrativo Certificado"),
        ("Fase 10: Soporte y Mantenimiento", "Continuo", "Semana 17 - 20+", "Monitoreo, Backups y Optimización Permanente")
    ]
    for r_idx, (f, dur, per, ent) in enumerate(g_rows):
        cf, cd, cp, ce = gantt_tbl.rows[r_idx + 1].cells
        cf.paragraphs[0].add_run(f).bold = True
        cd.paragraphs[0].add_run(dur)
        cp.paragraphs[0].add_run(per)
        ce.paragraphs[0].add_run(ent)
        set_cell_margins(cf, top=60, bottom=60, left=80, right=80)
        set_cell_margins(cd, top=60, bottom=60, left=80, right=80)
        set_cell_margins(cp, top=60, bottom=60, left=80, right=80)
        set_cell_margins(ce, top=60, bottom=60, left=80, right=80)
        if r_idx % 2 == 1:
            set_cell_background(cf, "F1F8E9")
            set_cell_background(cd, "F1F8E9")
            set_cell_background(cp, "F1F8E9")
            set_cell_background(ce, "F1F8E9")
    set_table_borders(gantt_tbl)
    
    doc.add_page_break()

    # -------------------------------------------------------------
    # SECCIÓN H: DISEÑO DEL SISTEMA UML (MODELADO COMPLETO)
    # -------------------------------------------------------------
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(18)
    h1.paragraph_format.space_after = Pt(8)
    r1 = h1.add_run("h. Diseño del Sistema UML")
    r1.font.size = Pt(18)
    r1.font.bold = True
    r1.font.color.rgb = COLOR_PRIMARY
    
    p = doc.add_paragraph()
    p.add_run(
        "El modelado formal del sistema se especifica mediante diagramas estandarizados bajo el Lenguaje Unificado de Modelado "
        "(UML) y diagramas relacionales, abarcando la perspectiva estructural (clases, bases de datos), la funcional "
        "(casos de uso) y la de comportamiento e interacción temporal (secuencia, estados y actividades)."
    )
    
    # --- h.1 Diagrama de Casos de Uso ---
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(6)
    r2 = h2.add_run("Diagrama de Casos de Uso UML")
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_SECONDARY
    
    p = doc.add_paragraph()
    p.add_run(
        "Modela las fronteras del sistema, los roles organizacionales (actores) y las funciones clave a las que cada uno "
        "tiene acceso con relaciones de inclusión `<<include>>` para validaciones críticas:"
    )
    
    # Diagrama 4: Casos de Uso
    cu_path = generar_diagrama_casos_uso()
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(cu_path, width=Inches(6.4))
    p_caption = doc.add_paragraph()
    p_caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap = p_caption.add_run("Figura 4: Diagrama de Casos de Uso UML con Actores y Límites del Sistema")
    r_cap.font.size = Pt(9.5)
    r_cap.font.italic = True
    r_cap.font.color.rgb = COLOR_MUTED

    # --- h.2 Diagrama de Clases UML ---
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    r2 = h2.add_run("Diagrama de Clases UML (Estructura Orientada a Objetos)")
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_SECONDARY
    
    p = doc.add_paragraph()
    p.add_run(
        "Representa la estructura interna de los modelos Django orientados a objetos, destacando la herencia generalizada "
        "desde la clase abstracta `ModeloTextoNormalizado` que asegura la sanitización y normalización automática de datos:"
    )
    
    # Diagrama 5: Clases
    clases_path = generar_diagrama_clases()
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(clases_path, width=Inches(6.4))
    p_caption = doc.add_paragraph()
    p_caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap = p_caption.add_run("Figura 5: Diagrama de Clases UML - Jerarquía de Herencia y Métodos del Modelo")
    r_cap.font.size = Pt(9.5)
    r_cap.font.italic = True
    r_cap.font.color.rgb = COLOR_MUTED

    # --- h.3 Diagrama Entidad-Relación (DER) ---
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    r2 = h2.add_run("Diagrama Entidad-Relación (DER)")
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_SECONDARY
    
    p = doc.add_paragraph()
    p.add_run(
        "Modela la estructura de tablas relacionales en la base de datos (PostgreSQL/SQLite), vinculando la maquinaria con "
        "sus despachos de combustible, registros de boletas, órdenes de trabajo y controles de servicio:"
    )
    
    # Diagrama 6: DER
    der_path = generar_diagrama_der()
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(der_path, width=Inches(6.4))
    p_caption = doc.add_paragraph()
    p_caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap = p_caption.add_run("Figura 6: Diagrama Entidad-Relación (DER) del Modelo de Base de Datos")
    r_cap.font.size = Pt(9.5)
    r_cap.font.italic = True
    r_cap.font.color.rgb = COLOR_MUTED

    # --- h.4 Diagrama de Secuencia 1: Despacho Combustible ---
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    r2 = h2.add_run("Diagrama de Secuencia: Despacho de Combustible")
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_SECONDARY
    
    p = doc.add_paragraph()
    p.add_run(
        "Modela la interacción temporal y el intercambio de mensajes para la emisión de vales de combustible y débito de inventario:"
    )
    
    # Diagrama 7: Secuencia Combustible
    sec_path = generar_diagrama_secuencia()
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(sec_path, width=Inches(6.4))
    p_caption = doc.add_paragraph()
    p_caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap = p_caption.add_run("Figura 7: Diagrama de Secuencia UML - Transacción de Despacho de Combustible")
    r_cap.font.size = Pt(9.5)
    r_cap.font.italic = True
    r_cap.font.color.rgb = COLOR_MUTED

    # --- h.5 Diagrama de Secuencia 2: Boletas Operativas de Campo ---
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    r2 = h2.add_run("Diagrama de Secuencia: Captura y Validación de Boleta Operativa")
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_SECONDARY
    
    p = doc.add_paragraph()
    p.add_run(
        "Ilustra el proceso reactivo mediante el cual el operador ingresa las boletas de labor en campo, el frontend calcula "
        "las horas efectivas y el backend valida la integridad del horómetro y la ausencia de duplicados:"
    )
    
    # Diagrama 8: Secuencia Operativo
    sec_op_path = generar_diagrama_secuencia_operativo()
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(sec_op_path, width=Inches(6.4))
    p_caption = doc.add_paragraph()
    p_caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap = p_caption.add_run("Figura 8: Diagrama de Secuencia UML - Captura y Validación de Boletas de Campo")
    r_cap.font.size = Pt(9.5)
    r_cap.font.italic = True
    r_cap.font.color.rgb = COLOR_MUTED

    # --- h.6 Diagrama de Estados UML ---
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    r2 = h2.add_run("Diagrama de Estados UML (State Machine)")
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_SECONDARY
    
    p = doc.add_paragraph()
    p.add_run(
        "Modela las transiciones de estado de la maquinaria agrícola (Disponible, En Campo, En Taller) y de las Órdenes "
        "de Mantenimiento (Pendiente, En Taller/En Proceso, Finalizada), garantizando la coherencia operativa:"
    )
    
    # Diagrama 9: Estados
    est_path = generar_diagrama_estados()
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(est_path, width=Inches(6.4))
    p_caption = doc.add_paragraph()
    p_caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap = p_caption.add_run("Figura 9: Diagrama de Estados UML - Ciclo de Vida de Maquinaria y Órdenes de Mantenimiento")
    r_cap.font.size = Pt(9.5)
    r_cap.font.italic = True
    r_cap.font.color.rgb = COLOR_MUTED

    # --- h.7 Diagrama de Actividades UML ---
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    r2 = h2.add_run("Diagrama de Actividades UML: Control Preventivo por Horómetro")
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_SECONDARY
    
    p = doc.add_paragraph()
    p.add_run(
        "Define el flujo de actividades y bifurcaciones condicionales que evalúan si una máquina agrícola requiere servicio "
        "preventivo, disparando automáticamente las alertas de semáforo:"
    )
    
    # Diagrama 10: Actividades
    act_path = generar_diagrama_actividades()
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(act_path, width=Inches(5.5))
    p_caption = doc.add_paragraph()
    p_caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap = p_caption.add_run("Figura 10: Diagrama de Actividades UML - Ciclo de Mantenimiento Preventivo por Horómetro")
    r_cap.font.size = Pt(9.5)
    r_cap.font.italic = True
    r_cap.font.color.rgb = COLOR_MUTED
    
    doc.add_page_break()

    # -------------------------------------------------------------
    # SECCIÓN I: DISEÑO DE INTERFACES
    # -------------------------------------------------------------
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(18)
    h1.paragraph_format.space_after = Pt(8)
    r1 = h1.add_run("i. Diseño de Interfaces")
    r1.font.size = Pt(18)
    r1.font.bold = True
    r1.font.color.rgb = COLOR_PRIMARY
    
    p = doc.add_paragraph()
    p.add_run(
        "El diseño de interfaces se organiza en torno a un mapa del sitio coherente, responsivo y adaptado para dispositivos "
        "móviles utilizados bajo condiciones de campo agrícola. A continuación se presenta el Diagrama de Navegación del Sistema:"
    )
    
    # Diagrama 11: Navegación
    nav_path = generar_diagrama_navegacion()
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(nav_path, width=Inches(6.4))
    p_caption = doc.add_paragraph()
    p_caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap = p_caption.add_run("Figura 11: Diagrama de Navegación y Arquitectura de Información (Site Map)")
    r_cap.font.size = Pt(9.5)
    r_cap.font.italic = True
    r_cap.font.color.rgb = COLOR_MUTED

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.add_run(
        "Para evidenciar la distribución espacial de los componentes y la ergonomía visual de las pantallas más críticas, "
        "se incluye la especificación de wireframes para el módulo de despacho de combustible y la matriz de semáforos de taller:"
    )

    # Diagrama 12: Wireframes
    wf_path = generar_diagrama_wireframes()
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(wf_path, width=Inches(6.4))
    p_caption = doc.add_paragraph()
    p_caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap = p_caption.add_run("Figura 12: Wireframes Arquitectónicos de Interfaces Críticas (Despacho de Combustible y Semáforo)")
    r_cap.font.size = Pt(9.5)
    r_cap.font.italic = True
    r_cap.font.color.rgb = COLOR_MUTED

    # Catálogo de Pantallas Detallado
    ui_screens = [
        {
            "name": "1. Módulo de Autenticación y Auditoría (login.html / signup.html)",
            "purpose": "Acceso seguro y registro de usuarios con auditoría de geolocalización.",
            "components": [
                "Formulario de inicio de sesión centrado con campos estilizados para usuario y contraseña.",
                "Script en JavaScript que solicita permiso para capturar coordenadas GPS (latitud y longitud) del dispositivo en el momento del login.",
                "Detección y categorización del tipo de dispositivo cliente (Móvil, Tableta, PC).",
                "Mensajes de validación y alerta ante credenciales incorrectas mediante notificaciones elegantes.",
                "Registro silencioso en segundo plano hacia la tabla LoginAttempt para auditoría de seguridad."
            ]
        },
        {
            "name": "2. Tablero de Control Principal y Menú de Módulos (home.html / modulos.html)",
            "purpose": "Hub central de navegación ergonómica y visualización de indicadores ejecutivos.",
            "components": [
                "Barra superior con identidad del sistema, nombre y rol del usuario activo, y botón de cierre de sesión.",
                "Tarjetas de acceso rápido (Cards) con microanimaciones hover para cada área: Operaciones de Campo, Combustibles, Mantenimiento, Catálogos y Usuarios.",
                "Métricas resumidas en vivo: Galones de diésel disponibles en tanques, tractores en campo, tractores en taller y alertas preventivas activas.",
                "Diseño adaptativo que se reorganiza automáticamente de cuadrícula de 3 columnas en escritorio a 1 columna en teléfonos."
            ]
        },
        {
            "name": "3. Módulo de Registros Operativos de Campo (registros_operativos.html / operacion.html)",
            "purpose": "Captura y consulta ágil de boletas de trabajo agrícola por finca, labor y tractor.",
            "components": [
                "Formulario estructurado en secciones colapsables: Datos de la Boleta, Datos de la Máquina/Operador, Ubicación (Finca/Lote) y Métricas de Rendimiento.",
                "Cálculo automático de horas trabajadas a partir del horómetro inicial y final con advertencia en tiempo real si el valor final es inconsistente.",
                "Autocompletado predictivo para labores agrícolas vinculadas al proceso correspondiente (siembra, fertilización o riego).",
                "Tabla de datos registrados con filtros rápidos por fecha, finca y número de boleta, permitiendo exportación de datos y edición controlada."
            ]
        },
        {
            "name": "4. Módulo de Control de Combustibles y Tanques (combustibles_despacho.html / combustibles_tanques.html)",
            "purpose": "Administración del inventario de diésel y despacho seguro de combustible a maquinaria.",
            "components": [
                "Generador automático del siguiente correlativo de vale de combustible (formato anual con numeración consecutiva).",
                "Selector de tanque con barra de progreso visual que ilustra el nivel de llenado actual frente a la capacidad máxima.",
                "Campo de horómetro de carga de la máquina que actualiza el historial del equipo.",
                "Validación visual inmediata: Si el operador intenta despachar más galones de los disponibles en el tanque seleccionado, la interfaz bloquea el envío y muestra un toast de advertencia."
            ]
        },
        {
            "name": "5. Módulo de Mantenimiento y Horómetros (mantenimiento_horometros.html / mantenimiento_ordenes.html)",
            "purpose": "Supervisión del semáforo preventivo y emisión de órdenes de trabajo de taller.",
            "components": [
                "Matriz de Semáforo Preventivo con tarjetas coloreadas: Verde (Al Día), Ámbar (Próximo a Vencer - a menos de 50 horas del límite) y Rojo (Vencido - requiere servicio inmediato).",
                "Botón de acción rápida en cada tarjeta para aperturar directamente una Orden de Mantenimiento con los datos de la máquina precargados.",
                "Formulario de orden de taller con selección de mecánico responsable, horómetro de ingreso, falla reportada, tipo de servicio y costo estimado en Quetzales (Q).",
                "Listado de órdenes con cambio de estado interactivo: 'Pendiente' → 'En Taller' → 'Finalizada'."
            ]
        },
        {
            "name": "6. Módulo de Catálogos Maestros y Configuración (configuracion_catalogos.html)",
            "purpose": "Mantenimiento centralizado de tablas maestras con normalización automática de datos.",
            "components": [
                "Pestañas de navegación para: Maquinaria, Proveedores, Empleados, Bodegas, Artículos, Cuentas Contables y Variedades de Cultivo.",
                "Formularios modales para agregar y editar registros sin recargar la página completa.",
                "Validación estricta de formatos: 13 dígitos numéricos para CUI de empleados, NIT de proveedores y 12 dígitos para cuentas contables.",
                "Normalización instantánea de texto en el frontend para retroalimentación visual al usuario."
            ]
        },
        {
            "name": "7. Sistema Centralizado de Notificaciones (notificaciones.js / NOTIFICACIONES_GUIA.md)",
            "purpose": "Retroalimentación interactiva y confirmaciones modales con identidad corporativa.",
            "components": [
                "Toast flotante en la esquina superior derecha con autocierre temporizado (Éxito verde #388e3c, Error rojo #d32f2f, Alerta ámbar #f57f17).",
                "Diálogos modales de confirmación con doble verificación antes de operaciones destructivas (eliminar registros o anular boletas).",
                "Indicadores visuales de validación de formulario en vivo (bordes verdes para campos válidos y rojos con texto explicativo para campos erróneos)."
            ]
        }
    ]
    
    for screen in ui_screens:
        h2 = doc.add_paragraph()
        h2.paragraph_format.space_before = Pt(12)
        h2.paragraph_format.space_after = Pt(4)
        r = h2.add_run(screen["name"])
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = COLOR_SECONDARY
        
        p_purp = doc.add_paragraph()
        r_lbl = p_purp.add_run("Objetivo: ")
        r_lbl.bold = True
        r_lbl.font.color.rgb = COLOR_PRIMARY
        p_purp.add_run(screen["purpose"])
        
        for comp in screen["components"]:
            bp = doc.add_paragraph(style='List Bullet')
            bp.paragraph_format.space_after = Pt(3)
            bp.add_run(comp)
            
    doc.add_page_break()

    # -------------------------------------------------------------
    # CONCLUSIONES Y RECOMENDACIONES
    # -------------------------------------------------------------
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(18)
    h1.paragraph_format.space_after = Pt(8)
    r1 = h1.add_run("Conclusiones y Recomendaciones Técnicas")
    r1.font.size = Pt(16)
    r1.font.bold = True
    r1.font.color.rgb = COLOR_PRIMARY
    
    conclusiones = [
        ("Viabilidad Demostrada:", "El análisis de factibilidad en sus cinco vertientes (técnica, operativa, económica, legal y ambiental) demuestra que el Sistema de Servicios Agrícolas es plenamente viable y estratégico, con un Retorno de Inversión (ROI) superior al 159% en su primer año de operación."),
        ("Solidez Arquitectónica y Modelado UML:", "La especificación mediante 12 diagramas formales (Arquitectura, Despliegue, Casos de Uso, Clases, DER, Secuencia, Estados, Actividades, Navegación y Wireframes) garantiza la comprensión técnica unificada para desarrolladores, auditores y la gerencia."),
        ("Mitigación de Riesgos Operativos:", "La implementación del semáforo preventivo por horómetro y el control correlativo de vales de combustible resuelven los dos puntos críticos de fuga económica más severos del sector agropecuario: el descontrol de combustible y las averías catastróficas por servicios extemporáneos."),
        ("Recomendación de Despliegue Escalonado:", "Se aconseja iniciar la puesta en producción con un plan piloto de dos semanas en una finca representativa antes de expandir el uso a la totalidad de las operaciones agrícolas de la corporación."),
        ("Monitoreo Continuo y Respaldo:", "Se recomienda programar respaldos diarios de la base de datos a las 23:00 horas y mantener activa la auditoría de accesos con geolocalización para proteger la integridad operativa.")
    ]
    for c_tit, c_txt in conclusiones:
        p_c = doc.add_paragraph(style='List Bullet')
        r = p_c.add_run(c_tit + " ")
        r.bold = True
        r.font.color.rgb = COLOR_PRIMARY
        p_c.add_run(c_txt)
        
    doc_path = os.path.join(OUTPUT_DIR, "Documento_Especificacion_Sistema_Servicios_Agricolas.docx")
    doc.save(doc_path)
    return doc_path

if __name__ == "__main__":
    print("Iniciando generación de documento y 12 diagramas UML...")
    final_path = crear_documento()
    print(f"Documento enriquecido generado exitosamente en: {final_path}")
