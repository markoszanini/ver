import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from organigrama.models import Area, Direccion, Departamento, Division, Subdivision, Seccion, Oficina

# REGIO_AREAS
areas_data = [
    (1, 'Área Legal y Técnica'),
    (21, 'Área de Desarrollo y Bienestar'),
    (22, 'Área de Economía y Finanzas'),
    (3, 'Área de Planificación Territorial'),
    (24, 'Área de Producción, Ciencia y Tecnología'),
    (2, 'Área de Control y Seguridad'),
    (23, 'Área de Gobierno y Gestión'),
]
for id_area, nombre in areas_data:
    Area.objects.update_or_create(id_area=id_area, defaults={'nombre': nombre})

# REGIO_DIRECCIONES
direcciones_data = [
    (4, 21, 'Dirección de Desarrollo Social'),
    (2, 23, 'Coordinador Área de Gobierno y Gestión'),
    (25, 21, 'Dirección de Deporte'),
    (1, 23, 'Community Manager'),
    (21, 24, 'Coordinación Operativa'),
    (22, 3, 'Dirección General y Planificación Urbana'),
    (3, 1, 'Dirección de Asuntos Jurídicos'),
    (24, 21, 'Dirección de Cultura'),
    (26, 24, 'Dirección de Innovación y Tecnología'),
    (23, 1, 'Dirección de Administración de Gobierno'),
]
for id_dir, id_area, nombre in direcciones_data:
    Direccion.objects.update_or_create(id_direccion=id_dir, defaults={'area_id': id_area, 'nombre': nombre})

# REGIO_DEPARTAMENTOS
deptos_data = [
    (23, 23, None, 'Departamento Secretaría'),
    (7, 21, 24, 'Departamento de Administración y Gestion de Cultura y Educación'),
    (26, 21, 24, 'Departamento de Administración y Planificación de la Cultura y las Artes del Teatro Dante'),
    (28, 22, None, 'Departamento de Contaduría'),
    (8, 21, 25, 'Departamento de Deportes'),
    (12, 2, None, 'Departamento de Seguridad Vial'),
    (1, 21, 4, 'CAF - Centro de Atención a Familias'),
    (5, 23, None, 'Departamento Tribunal de Faltas'),
    (10, 22, None, 'Departamento de Ingresos Públicos'),
    (30, 3, None, 'Departamento de Obras Privadas y Catastro'),
    (13, 22, None, 'Departamento de Tesorería'),
    (31, 21, 4, 'Hogar Taller y Granja Protegido Municipal'),
    (21, 23, None, 'Departamento Habilitaciones'),
    (25, 21, 4, 'Departamento de Acción Social'),
    (11, 2, None, 'Departamento de Inspección General'),
    (29, 3, None, 'Departamento de Mantenimiento y Producción'),
    (32, 23, None, 'Seguridad Alimentaria'),
    (3, 23, None, 'Departamento Mesa de Entradas Archivo y Censo'),
    (22, 23, None, 'Departamento Obras por Administración Cementerio'),
    (4, 23, None, 'Departamento Personal'),
    (24, 23, None, 'Departamento Sistema de Computación de Datos'),
    (6, 23, None, 'Departamento Tránsito'),
    (9, 3, None, 'Departamento de Ejecución de Obras por Administración'),
    (2, 22, None, 'Contador General'),
    (27, 22, None, 'Departamento de Compras y Suministros'),
]
for id_depto, id_area, id_dir, nombre in deptos_data:
    Departamento.objects.update_or_create(id_departamento=id_depto, defaults={'area_id': id_area, 'direccion_id': id_dir, 'nombre': nombre})

# REGIO_DIVISIONES
divisiones_data = [
    (3, 27, 'División Compras y Suministros'),
    (1, 29, 'Alumbrado'),
    (2, 30, 'División Catastro'),
    (22, 29, 'Parque Automotor'),
    (21, 25, 'División de Servicio Social'),
]
for id_div, id_depto, nombre in divisiones_data:
    Division.objects.update_or_create(id_division=id_div, defaults={'departamento_id': id_depto, 'nombre': nombre})

# REGIO_SUBDIVISIONES
subdiv_data = [
    (4, None, 'Subdivisión Obras', 9, 3),
    (21, None, 'Subdivisión Parques y Paseos', 29, 3),
    (2, None, 'Subdivisión Herrería y Carpintería', 29, 3),
    (5, None, 'Taxis y Remises', None, 23),
    (3, None, 'Subdivisión Mecánica', 29, 3),
    (1, None, 'Subdivisión Albañilería', 29, 3),
    (22, None, 'Taxis y Remises', None, None),
]
for id_subdiv, id_div, nombre, id_depto, id_area in subdiv_data:
    Subdivision.objects.update_or_create(id_subdivision=id_subdiv, defaults={'division_id': id_div, 'departamento_id': id_depto, 'area_id': id_area, 'nombre': nombre})

# REGIO_SECCIONES
sec_data = [
    (21, None, 'Sección Albañilería', 4, None),
    (2, None, 'Sección Aguas Corrientes', 4, None),
    (22, None, 'Sección Cementerio', None, 29),
    (5, None, 'Sección Terminal de Ómnibus', None, 29),
    (3, None, 'Sección Barrido', None, 29),
    (4, None, 'Sección Cloacas', 4, None),
    (1, None, 'Sección Acopio de Materiales', 4, None),
]
for id_sec, id_div, nombre, id_subdiv, id_depto in sec_data:
    Seccion.objects.update_or_create(id_seccion=id_sec, defaults={'division_id': id_div, 'subdivision_id': id_subdiv, 'departamento_id': id_depto, 'nombre': nombre})

# REGIO_OFICINAS
ofi_data = [
    (4, 'Complejo Cultural y Educativo Benito Quinquela Martín', 21, 24, None),
    (7, 'Equipo Municipal Interdisciplinario de Secundario', 21, 24, None),
    (8, 'Oficina de Administración de Maestranza y Reclamos', 3, None, None),
    (9, 'Parques y Paseos', 3, None, None),
    (10, 'Servicio de Orientación Vocacional', 21, 24, None),
    (27, 'OMIC', 23, None, None),
    (11, 'Sistema de Cámaras', 2, None, None),
    (32, 'Área de Igualdad Género y Diversidad', 21, 4, 21),
    (21, 'Biblioteca Pública Municipal', 21, 24, None),
    (23, 'EMAP', 21, 24, None),
    (28, 'Profesores Banda Cesar Mastroiacovo', 21, 24, None),
    (12, 'Área de la Mujer', 21, 4, 21),
    (1, 'APRECOD', 21, 4, 21),
    (2, 'Centro Educativo y Cultural Eduardo Bracaccini', 21, 24, None),
    (3, 'Centro de Día Horizonte', 21, 4, 21),
    (22, 'Coro Infantil', 21, 24, None),
    (24, 'Equipo Local de Niñez', 21, 4, 21),
    (31, 'Taller Municipal de Teatro para las Infancias y Jóvenes', 21, 24, None),
    (5, 'Complejo Vivienda Tercera Edad', 21, 4, 21),
    (6, 'Coro Municipal Voces Argentinas', 21, 24, None),
    (25, 'Museo Archivo Histórico Municipal Don Santos Tosticarelli', 21, 24, None),
    (26, 'Notificaciones', 23, None, None),
    (29, 'Protección y Sanidad Animal', 23, None, None),
    (30, 'Punto Violeta', 21, 4, 21),
]
for id_ofi, nombre, id_area, id_dir, id_div in ofi_data:
    Oficina.objects.update_or_create(id_oficina=id_ofi, defaults={'area_id': id_area, 'direccion_id': id_dir, 'division_id': id_div, 'nombre': nombre})

print("Importacion de organigrama completada.")
