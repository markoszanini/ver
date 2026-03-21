import os
import django

# Setup django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from empleo.models import RubroEmpleo, PuestoEmpleo

rubros_data = [
    (2, 'Operario de Planta', 'S'),
    (3, 'Tornería / CNC', 'S'),
    (5, 'Electricidad Industrial', 'S'),
    (25, 'Refrigeración / HVAC', 'S'),
    (9, 'Administrativo / Contable', 'S'),
    (11, 'Salud', 'S'),
    (13, 'Agro / Campo', 'S'),
    (21, 'Metalúrgica / Soldadura', 'S'),
    (7, 'Electricidad Domiciliaria', 'S'),
    (26, 'Atención al Público', 'S'),
    (27, 'Ventas / Comercial', 'S'),
    (10, 'Logística / Depósito', 'S'),
    (14, 'Otros Oficios', 'S'),
    (41, 'Servicio Doméstico', 'S'),
    (23, 'Mecánica Automotriz', 'S'),
    (6, 'Construcción / Albañilería', 'S'),
    (24, 'Gasista / Plomería', 'S'),
    (29, 'Educación', 'S'),
    (12, 'Tecnología / Sistemas', 'S'),
    (4, 'Técnico / Taller', 'S') # Missing rubro 4 added
]

for r_id, desc, act in rubros_data:
    obj, created = RubroEmpleo.objects.update_or_create(
        id_rubro=r_id,
        defaults={'descripcion': desc, 'activo': act}
    )

puestos_data = [
    (2, 2, 'Operario de línea', 'S'),
    (5, 4, 'Herrero', 'S'),
    (24, 5, 'Instrumentista', 'S'),
    (27, 11, 'Acompañante terapéutico', 'S'),
    (12, 13, 'Peón rural', 'S'),
    (13, 13, 'Tractorista', 'S'),
    (28, 21, 'Soldador', 'S'),
    (16, 27, 'Telemarketer', 'S'),
    (32, 10, 'Depósito', 'S'),
    (18, 14, 'Carga/descarga', 'S'),
    (20, 6, 'Albañil', 'S'),
    (33, 6, 'Oficial', 'S'),
    (41, 6, 'Medio oficial', 'S'),
    (34, 24, 'Gasista', 'S'),
    (45, 12, 'Programador', 'S'),
    (61, 2, 'Operario general', 'S'),
    (84, 4, 'Operario de taller', 'S'),
    (85, 4, 'Lijador', 'S'),
    (89, 6, 'Ayudante de albañil', 'S')
]

for p_id, r_id, desc, act in puestos_data:
    rubro = RubroEmpleo.objects.get(id_rubro=r_id)
    obj, created = PuestoEmpleo.objects.update_or_create(
        id_puesto=p_id,
        defaults={'rubro': rubro, 'descripcion': desc, 'activo': act}
    )

print("Datos cargados exitosamente.")
