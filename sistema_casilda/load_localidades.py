import os
import django

# Setup django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from portal.models import Localidad

localidades_data = [
    ('1', 'Casilda'),
    ('2', 'Arteaga'),
    ('3', 'Arequito'),
    ('4', 'Berabevú'),
    ('5', 'Chañar Ladeado'),
    ('6', 'Gödeken'),
    ('7', 'Sanford'),
    ('21', 'Bigand'),
    ('22', 'Chabás'),
    ('23', 'Los Molinos'),
    ('24', 'Villada'),
    ('25', 'Fuentes'),
    ('100', 'Rosario'),
    ('101', 'Venado Tuerto'),
    ('102', 'San Lorenzo'),
    ('103', 'Villa Constitución'),
    ('104', 'Firmat'),
    ('105', 'Roldán'),
    ('106', 'Funes'),
    ('107', 'Pujato'),
    ('108', 'Zavalla'),
    ('109', 'Pérez'),
    ('8', 'Otro')
]

count = 0
for loc_id, nombre in localidades_data:
    # We use update_or_create to ensure we don't duplicate but update if name changes
    # The id might not match the original INT but the name is the key for the user
    # Actually, many models now point to portal.Localidad via FK (id).
    # If possible, we try to keep the IDs if we can, but since it's a new table...
    # We'll just create them and let Django assign IDs.
    obj, created = Localidad.objects.update_or_create(
        nombre=nombre,
        defaults={'nombre': nombre}
    )
    if created:
        count += 1

print(f"Sincronización de localidades completada. Se agregaron {count} nuevas ciudades.")
print(f"Total en tabla Localidad: {Localidad.objects.count()}")
