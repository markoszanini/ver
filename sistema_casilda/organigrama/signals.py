from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Funcionario

@receiver(post_save, sender=Funcionario)
def asignar_permisos_automaticos(sender, instance, created, **kwargs):
    user = instance.user
    
    if not user:
        return

    # Todos los empleados orgánicos deben tener mínimo acceso a la vista panel admin
    if not user.is_staff:
        user.is_staff = True
        user.save(update_fields=['is_staff'])

    # Evitamos alterar a los superusuarios (administradores maestros)
    if user.is_superuser:
        return

    # Limpiar permisos previos para regenerarlos ante un cambio
    user.user_permissions.clear()
    
    apps_permitidas = set()
    
    nombre_area = instance.area.nombre.lower() if instance.area else ""
    nombre_depto = instance.departamento.nombre.lower() if instance.departamento else ""

    # Regla 1: Área de Gobierno y Gestión + Departamento Tribunal de Faltas -> Multas
    if 'gobierno' in nombre_area and 'gesti' in nombre_area and 'falta' in nombre_depto:
        apps_permitidas.add('multas')
        
    # Regla 2: Área de Producción, Ciencia y Tecnología -> Apicultura, Empleo, Ferias
    if 'producc' in nombre_area and 'ciencia' in nombre_area:
        apps_permitidas.update(['apicultura', 'empleo', 'ferias'])

    # Regla 3: Rango de Secretario o Jefe en CUALQUIER área -> Compras y Expedientes
    if instance.rango in ['SECRETARIO', 'JEFE']:
        apps_permitidas.update(['compras', 'expedientes'])

    # Otorgar los permisos resultantes
    if apps_permitidas:
        for app_label in apps_permitidas:
            content_types = ContentType.objects.filter(app_label=app_label)
            if not content_types.exists():
                continue # Evitar crashear si la app aún no fue programada (ej. compras)
            
            perms = Permission.objects.filter(content_type__in=content_types)
            
            for perm in perms:
                # El Rango JEFE habilita permisos de borrado permanente (delete_).
                if perm.codename.startswith('delete_'):
                    if instance.rango == 'JEFE':
                        user.user_permissions.add(perm)
                else:
                    user.user_permissions.add(perm)

