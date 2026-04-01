import django
import os
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

def get_perms(app_label, model=None, actions=['view', 'add', 'change', 'delete']):
    """Helper to get permissions by app and model."""
    if model:
        cts = ContentType.objects.filter(app_label=app_label, model=model)
    else:
        cts = ContentType.objects.filter(app_label=app_label)
    
    perms = []
    for action in actions:
        perms.extend(list(Permission.objects.filter(content_type__in=cts, codename__startswith=action)))
    return perms

def create_groups():
    print("Creando grupos de gestión...")
    
    # 1. Gestión de Turnos
    g_turnos, _ = Group.objects.get_or_create(name='MUNI_Gestión_Turnos')
    g_turnos.permissions.set(get_perms('turnos'))
    
    # 2. Gestión de Expedientes (Consulta/Carga) - No pueden editar ni borrar el expediente en sí, solo cargar movimientos
    g_exp_basic, _ = Group.objects.get_or_create(name='MUNI_Expedientes_Consulta_Carga')
    exp_perms = get_perms('expedientes', model='expediente', actions=['view', 'add'])
    mov_perms = get_perms('expedientes', model='movimientoexpediente', actions=['view', 'add'])
    g_exp_basic.permissions.set(exp_perms + mov_perms)
    
    # 3. Gestión de Expedientes (Administración) - Full access
    g_exp_admin, _ = Group.objects.get_or_create(name='MUNI_Expedientes_Administración')
    g_exp_admin.permissions.set(get_perms('expedientes'))
    
    # 4. Gestión de Multas
    g_multas, _ = Group.objects.get_or_create(name='MUNI_Gestión_Multas')
    g_multas.permissions.set(get_perms('multas'))
    
    # 5. Gestión de Producción (Combo: Apicultura, Empleo, Ferias, Capacitaciones)
    g_prod, _ = Group.objects.get_or_create(name='MUNI_Gestión_Producción')
    prod_perms = get_perms('apicultura') + get_perms('empleo') + get_perms('ferias') + get_perms('capacitaciones')
    g_prod.permissions.set(prod_perms)
    
    # 6. Gestión de Compras
    g_compras, _ = Group.objects.get_or_create(name='MUNI_Gestión_Compras')
    g_compras.permissions.set(get_perms('compras'))
    
    return {
        'turnos': g_turnos,
        'exp_basic': g_exp_basic,
        'exp_admin': g_exp_admin,
        'multas': g_multas,
        'produccion': g_prod,
        'compras': g_compras
    }

def assign_users(groups):
    assignments = {
        'eugenia.nin': ['turnos', 'exp_basic', 'compras'],
        'mariana.martinez': ['exp_admin', 'compras'],
        'emilio.ardiani': ['multas', 'exp_basic', 'compras'],
        'alicia.ordasso': ['produccion', 'exp_basic', 'compras']
    }
    
    for username, group_keys in assignments.items():
        try:
            user = User.objects.get(username=username)
            user.groups.clear()
            for key in group_keys:
                user.groups.add(groups[key])
            
            # Asegurar Staff
            if not user.is_staff:
                user.is_staff = True
            user.save()
            print(f"Roles asignados correctamente a {username}")
        except User.DoesNotExist:
            print(f"AVISO: El usuario '{username}' no existe en la base de datos.")

if __name__ == "__main__":
    groups = create_groups()
    assign_users(groups)
    print("Proceso finalizado.")
