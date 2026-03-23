from django.db import models
from portal.models import Vecino

class Capacitacion(models.Model):
    TIPO_AREA_CHOICES = [
        ('ASAC', 'Seguridad Alimentaria (ASAC)'),
        ('PRODUCCION', 'Área de Producción, Ciencia y Tecnología'),
        ('QUINQUELA', 'Cultura (Quinquela Martín)'),
    ]
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(help_text="Detalles del curso, horarios, lugar, etc.")
    area_responsable = models.CharField(max_length=20, choices=TIPO_AREA_CHOICES)
    fecha_inicio = models.DateField()
    cupo_maximo = models.IntegerField(help_text="Cantidad máxima de inscriptos permitidos. Cuando se alcanza, la inscripción se cierra automáticamente.")
    estado_inscripcion = models.CharField(max_length=20, choices=[('ABIERTA', 'Abierta'), ('CERRADA', 'Cerrada')], default='ABIERTA')
    
    class Meta:
        verbose_name = "Capacitación / Taller"
        verbose_name_plural = "Capacitaciones y Talleres"
        
    def __str__(self):
        return f"{self.nombre} ({self.get_area_responsable_display()})"
    
    @property
    def cupos_disponibles(self):
        inscriptos = self.inscripciones.filter(estado='INSCRIPTO').count()
        return max(0, self.cupo_maximo - inscriptos)
        
    @property
    def cupos_ocupados(self):
        return self.inscripciones.filter(estado='INSCRIPTO').count()

    def verificar_y_cerrar_cupo(self):
        if self.estado_inscripcion == 'ABIERTA' and self.cupos_disponibles <= 0:
            self.estado_inscripcion = 'CERRADA'
            self.save(update_fields=['estado_inscripcion'])


class Inscripcion(models.Model):
    ESTADO_CHOICES = [
        ('INSCRIPTO', 'Inscripto'),
        ('CANCELADO', 'Cancelado por el Vecino o Autoridad'),
        ('FINALIZADO', 'Finalizó/Asistió'),
    ]
    capacitacion = models.ForeignKey(Capacitacion, on_delete=models.CASCADE, related_name='inscripciones')
    vecino = models.ForeignKey(Vecino, on_delete=models.CASCADE, related_name='capacitaciones')
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='INSCRIPTO')

    class Meta:
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"
        unique_together = ('capacitacion', 'vecino')

    def __str__(self):
        return f"[{self.get_estado_display()}] {self.vecino.user.first_name} en {self.capacitacion.nombre}"
