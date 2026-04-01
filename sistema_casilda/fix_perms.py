import django
import os
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from organigrama.models import Funcionario

print("Iniciando reparación de permisos para RRHH...")

# Obtener todos los funcionarios que cumplen el criterio
funcionarios = Funcionario.objects.all()
cts = ContentType.objects.filter(app_label='recursos_humanos')
perms = list(Permission.objects.filter(content_type__in=cts))

count = 0
for f in funcionarios:
    if not f.user: continue
    
    area_nom = f.area.nombre.lower() if f.area else ""
    dep_nom = f.departamento.nombre.lower() if f.departamento else ""
    
    if f.rango == 'JEFE' and 'gobierno' in area_nom and 'personal' in dep_nom:
        print(f"Asignando permisos a {f.user.username}...")
        for perm in perms:
            f.user.user_permissions.add(perm)
        
        # Asegurar Staff
        if not f.user.is_staff:
            f.user.is_staff = True
            f.user.save()
        count += 1

print(f"Proceso finalizado. Se actualizaron {count} usuarios.")
