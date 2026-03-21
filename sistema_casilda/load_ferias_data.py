import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from ferias.models import RubroFeriante, SubrubroFeriante

# Complete list of subrubros
subrubros_data = [
    (23, 1, 'Chocolates'),
    (32, 3, 'Bijou'),
    (35, 4, 'Piedras'),
    (14, 5, 'Madera / Carpintería - Metales / Herrería'),
    (38, 5, 'Papel'),
    (44, 8, 'Juegos de mesa'),
    (5, 1, 'Bebidas artesanales'),
    (25, 1, 'Hierbas naturales'),
    (26, 2, 'Pintura'),
    (29, 3, 'Ropa artesanal'),
    (11, 4, 'Aromas textiles'),
    (33, 4, 'Spray áuricos'),
    (39, 5, 'Duendes, atrapasueños, muñecos, etc'),
    (16, 5, 'Plantas ornamentales'),
    (17, 6, 'Mates'),
    (63, 8, 'Pines'),
    (1, 1, 'Panificados'),
    (21, 1, 'Dulces artesanales'),
    (2, 1, 'Alfajores'),
    (22, 1, 'Mermeladas'),
    (3, 1, 'Pastelería'),
    (9, 3, 'Bolsos y mochilas'),
    (10, 3, 'Marroquinería'),
    (31, 3, 'Accesorios textiles'),
    (13, 4, 'Cosmética natural'),
    (19, 6, 'Cremas y cosméticos'),
    (42, 7, 'Proyecto social'),
    # --- Los que faltaban ---
    (62, 8, 'Calcomanías e imanes'),
    (64, 8, 'Objetos 3D'),
    (43, 8, 'Sellos'),
    (66, 1, 'Huerta orgánica'),
    (24, 1, 'Salames y quesos artesanales'),
    (8, 2, 'Calcomanías e imanes'),
    (28, 2, 'Diseño gráfico'),
    (34, 4, 'Sahumerios'),
    (37, 5, 'Tejido'),
    (18, 6, 'Perfumes alternativos'),
    (20, 6, 'Artículos de bazar'),
    (41, 7, 'Cooperativa'),
    (4, 1, 'Comidas regionales'),
    (6, 1, 'Artículos libres de gluten'),
    (7, 2, 'Ilustración'),
    (27, 2, 'Fotografía'),
    (30, 3, 'Calzados'),
    (12, 4, 'Velas'),
    (15, 5, 'Cerámica – Porcelana fría'),
    (36, 5, 'Vidrio'),
    (40, 7, 'ONG'),
    (61, 7, 'Institucione educativa'),
    (65, 8, 'Artículos retro'),
]

count = 0
for s_id, r_id, nombre in subrubros_data:
    rubro = RubroFeriante.objects.filter(id_rubro=r_id).first()
    if rubro:
        _, created = SubrubroFeriante.objects.update_or_create(
            id_subrubro=s_id, defaults={'rubro': rubro, 'nombre': nombre}
        )
        if created:
            count += 1

print(f"Nuevos subrubros agregados: {count}. Total en base: {SubrubroFeriante.objects.count()}")
