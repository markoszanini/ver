from django.db import models
from django.contrib.auth.models import User
from portal.models import Vecino
from organigrama.models import Area, Oficina

class Reclamo(models.Model):
    AREA_CHOICES = [
        ('Inspección', 'Inspección'),
        ('Mantenimiento', 'Mantenimiento'),
        ('Salud', 'Salud'),
    ]

    TIPO_CHOICES = [
        # Inspección
        ('Irregularidades en obras', 'Irregularidades en obras'),
        ('Actividad comercial irregular', 'Actividad comercial irregular'),
        ('Poda no autorizada', 'Poda no autorizada'),
        ('Sustancias peligrosas', 'Sustancias peligrosas'),
        ('Ocupación de espacios públicos', 'Ocupación de espacios públicos'),
        ('Aguas servidas', 'Aguas servidas'),
        ('Micro basural', 'Micro basural'),
        ('Accesibilidad para personas con discapacidad', 'Accesibilidad para personas con discapacidad'),
        # Mantenimiento
        ('Arreglo calle de ripio', 'Arreglo calle de ripio'),
        ('Boca de tormenta obstruída', 'Boca de tormenta obstruída'),
        ('Apertura y limpieza de cuneta', 'Apertura y limpieza de cuneta'),
        ('Caminos rurales', 'Caminos rurales'),
        ('Colocación o reposición de tubos media caña cuneta', 'Colocación o reposición de tubos media caña cuneta'),
        ('Daños en espacios públicos', 'Daños en espacios públicos'),
        ('Arreglo calle de tierra', 'Arreglo calle de tierra'),
        ('Colocación de brea', 'Colocación de brea'),
        # Salud
        ('Plagas y vectores en espacios públicos', 'Plagas y vectores en espacios públicos'),
        ('Plagas y vectores en propiedad privada', 'Plagas y vectores en propiedad privada'),
    ]

    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('En Proceso', 'En Proceso'),
        ('Resuelto', 'Resuelto'),
        ('Rechazado', 'Rechazado'),
    ]

    vecino = models.ForeignKey(Vecino, on_delete=models.CASCADE, related_name='reclamos')
    area = models.CharField(max_length=50, choices=AREA_CHOICES)
    tipo_reclamo = models.CharField(max_length=100, choices=TIPO_CHOICES)
    
    calle = models.CharField(max_length=100, verbose_name="Calle")
    numero = models.CharField(max_length=20, verbose_name="Número o altura")
    barrio = models.CharField(max_length=100, verbose_name="Barrio del reclamo")
    
    observacion = models.TextField(verbose_name="Observación / Detalles")
    foto = models.ImageField(upload_to='reclamos_fotos/', blank=True, null=True, verbose_name="Foto Adjunta")
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Reclamo"
        verbose_name_plural = "Reclamos"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.tipo_reclamo} - {self.vecino.user.get_full_name()} ({self.get_estado_display()})"

class PaseReclamo(models.Model):
    reclamo = models.ForeignKey(Reclamo, on_delete=models.CASCADE, related_name='pases')
    fecha_pase = models.DateTimeField(auto_now_add=True)
    area_destino = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)
    oficina_destino = models.ForeignKey(Oficina, on_delete=models.SET_NULL, null=True, blank=True)
    observacion = models.TextField(blank=True, null=True, verbose_name="Motivo del pase")
    usuario_emisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    leido_por_vecino = models.BooleanField(default=False, verbose_name="Leído por el vecino")

    class Meta:
        verbose_name = "Pase de Reclamo"
        verbose_name_plural = "Pases de Reclamo"
        ordering = ['-fecha_pase']
        
    def __str__(self):
        return f"Pase: {self.reclamo.id} -> {self.area_destino or self.oficina_destino}"

class MensajeReclamo(models.Model):
    reclamo = models.ForeignKey(Reclamo, on_delete=models.CASCADE, related_name='mensajes')
    fecha = models.DateTimeField(auto_now_add=True)
    mensaje = models.TextField()
    es_empleado = models.BooleanField(default=False)
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    leido = models.BooleanField(default=False, verbose_name="Leído")

    class Meta:
        verbose_name = "Mensaje de Reclamo"
        verbose_name_plural = "Mensajes de Reclamo"
        ordering = ['fecha']

    def __str__(self):
        return f"Mensaje en Reclamo #{self.reclamo.id}"
