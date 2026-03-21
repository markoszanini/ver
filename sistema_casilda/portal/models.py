from django.db import models
from django.contrib.auth.models import User

class Vecino(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vecino_profile')
    dni = models.CharField(max_length=20, unique=True, verbose_name="DNI")
    telefono = models.CharField(max_length=50, blank=True, null=True, verbose_name="Teléfono")
    domicilio = models.CharField(max_length=200, blank=True, null=True, verbose_name="Domicilio")
    
    class Meta:
        verbose_name = "Vecino"
        verbose_name_plural = "Vecinos"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.dni})"
