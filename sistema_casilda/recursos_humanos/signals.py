from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from organigrama.models import Funcionario
from .models import ReciboSueldo, Vacaciones, NovedadRRHH

@receiver(post_save, sender=Funcionario)
def asignar_permisos_rrhh(sender, instance, **kwargs):
    """
    Asigna permisos de gestión de RRHH automáticamente a los Jefes de Personal.
    """
    if not instance.user:
        return

    area_nom = instance.area.nombre.lower() if instance.area else ""
    dep_nom = instance.departamento.nombre.lower() if instance.departamento else ""
    
    # Criterio: Jefe de Gobierno/Personal
    es_jefe_rrhh = instance.rango == 'JEFE' and 'gobierno' in area_nom and 'personal' in dep_nom

    if es_jefe_rrhh:
        # Obtener content types de RRHH
        cts = ContentType.objects.filter(app_label='recursos_humanos')
        perms = Permission.objects.filter(content_type__in=cts)
        
        # Asignar permisos al usuario
        for perm in perms:
            instance.user.user_permissions.add(perm)
        
        # Asegurarse de que sea Staff para entrar al admin
        if not instance.user.is_staff:
            instance.user.is_staff = True
            instance.user.save()
            
        print(f"Permisos de RRHH asignados a {instance.user.username}")
