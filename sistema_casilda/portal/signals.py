from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Vecino
from expedientes.models import Expediente

@receiver(post_save, sender=Vecino)
def vincular_expedientes_retroactivos(sender, instance, created, **kwargs):
    if created:
        # Al crear un vecino, buscamos expedientes que tengan su DNI cargado manualmente
        # y los vinculamos a su nuevo perfil.
        expedientes_pendientes = Expediente.objects.filter(
            dni_titular_manual=instance.dni,
            vecino_titular__isnull=True
        )
        for exp in expedientes_pendientes:
            exp.vecino_titular = instance
            exp.save()
