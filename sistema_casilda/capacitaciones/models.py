from django.db import models
from portal.models import Vecino

class Capacitacion(models.Model):
    TIPO_AREA_CHOICES = [
        ('ASAC', 'Seguridad Alimentaria (ASAC)'),
        ('PRODUCCION', 'Área de Producción, Ciencia y Tecnología'),
        ('QUINQUELA', 'Cultura (Quinquela Martín)'),
    ]
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    area_responsable = models.CharField(max_length=20, choices=TIPO_AREA_CHOICES)
    
    fecha_inicio = models.DateField()
    dias_dictado = models.CharField(max_length=100, verbose_name="Días de dictado", help_text="Ej: Lunes y Miércoles", blank=True, null=True)
    horarios = models.CharField(max_length=100, verbose_name="Horarios", help_text="Ej: 18:00 a 20:00 hs", blank=True, null=True)
    lugar = models.CharField(max_length=200, verbose_name="Lugar/Aula", blank=True, null=True)
    
    cupo_maximo = models.IntegerField(help_text="Cantidad máxima de inscriptos permitidos.")
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
    certificado = models.FileField(upload_to='capacitaciones/certificados/', blank=True, null=True, verbose_name="Certificado en PDF")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.capacitacion.verificar_y_cerrar_cupo()

    class Meta:
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"
        unique_together = ('capacitacion', 'vecino')

    def __str__(self):
        return f"[{self.get_estado_display()}] {self.vecino.user.first_name} en {self.capacitacion.nombre}"
