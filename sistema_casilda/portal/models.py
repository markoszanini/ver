from django.db import models
from django.contrib.auth.models import User

class Localidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    codigo_postal = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "Localidad"
        verbose_name_plural = "Localidades"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Vecino(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vecino_profile')
    dni = models.CharField(max_length=20, unique=True, verbose_name="DNI")
    telefono = models.CharField(max_length=50, blank=True, null=True, verbose_name="Teléfono")
    domicilio = models.CharField(max_length=200, blank=True, null=True, verbose_name="Domicilio")
    localidad = models.ForeignKey(Localidad, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Localidad")
    
    class Meta:
        verbose_name = "Vecino"
        verbose_name_plural = "Vecinos"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.dni})"

class Notificacion(models.Model):
    vecino = models.ForeignKey(Vecino, on_delete=models.CASCADE, related_name='notificaciones', verbose_name="Vecino")
    titulo = models.CharField(max_length=200, verbose_name="Título")
    mensaje = models.TextField(verbose_name="Mensaje")
    link = models.CharField(max_length=255, blank=True, null=True, verbose_name="Enlace opcional")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    leida = models.BooleanField(default=False, verbose_name="Leída")

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.titulo} - {self.vecino.user.username}"
