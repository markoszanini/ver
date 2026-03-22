from django.db import models
from django.core.exceptions import ValidationError
from portal.models import Vecino
from django.utils import timezone

class ConfiguracionTurno(models.Model):
    TIPO_CHOICES = [
        ('PSICOFISICO', 'Psicofísico'),
        ('LICENCIA', 'Licencia de Conducir'),
    ]
    tipo_turno = models.CharField(max_length=20, choices=TIPO_CHOICES, unique=True)
    hora_inicio = models.TimeField(default='07:00')
    hora_fin = models.TimeField(default='13:00')
    turnos_por_hora = models.IntegerField(default=4, help_text="Ej: 4 significa un turno cada 15 minutos exactos.")
    dias_habiles = models.CharField(max_length=50, default="0,1,2,3,4", help_text="0=Lunes, 4=Viernes. Separado por comas.")
    
    class Meta:
        verbose_name = "Configuración de Turnos"
        verbose_name_plural = "Configuraciones de Turnos"

    def __str__(self):
        return f"Configuración {self.get_tipo_turno_display()}"


class Turno(models.Model):
    TIPO_CHOICES = [
        ('PSICOFISICO', 'Psicofísico'),
        ('LICENCIA', 'Licencia de Conducir'),
    ]
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]
    
    vecino = models.ForeignKey(Vecino, on_delete=models.CASCADE, related_name='turnos')
    tipo_turno = models.CharField(max_length=20, choices=TIPO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    fecha = models.DateField()
    hora = models.TimeField()
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    
    # Datos adicionales para Licencia
    tipo_licencia = models.CharField(max_length=20, null=True, blank=True, help_text="Ej: A, B1, B2, C, etc.")
    vencimiento_licencia = models.DateField(null=True, blank=True, verbose_name="Fecha de Vencimiento de Licencia Actual")
    observaciones = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"
        unique_together = ('tipo_turno', 'fecha', 'hora')
        ordering = ['-fecha', 'hora']

    def __str__(self):
        return f"{self.get_tipo_turno_display()} - {self.vecino.user.first_name} {self.vecino.user.last_name} ({self.fecha} {self.hora})"

    def clean(self):
        if self.tipo_turno == 'LICENCIA':
            if not self.tipo_licencia:
                raise ValidationError({'tipo_licencia': 'El tipo de licencia es obligatorio para este turno.'})
            if not self.vencimiento_licencia:
                raise ValidationError({'vencimiento_licencia': 'La fecha de vencimiento es obligatoria para verificar renovación.'})
        super().clean()
