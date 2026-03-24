from django.db import models
from portal.models import Localidad

class RubroFeriante(models.Model):
    id_rubro = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Rubro")
    estado = models.CharField(max_length=20, default='ACTIVO', verbose_name="Estado")

    class Meta:
        verbose_name = "Rubro"
        verbose_name_plural = "Rubros"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class SubrubroFeriante(models.Model):
    id_subrubro = models.AutoField(primary_key=True)
    rubro = models.ForeignKey(RubroFeriante, on_delete=models.CASCADE, related_name='subrubros', verbose_name="Rubro")
    nombre = models.CharField(max_length=150, verbose_name="Nombre del Subrubro")

    class Meta:
        verbose_name = "Subrubro"
        verbose_name_plural = "Subrubros"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class CapacitacionFeriante(models.Model):
    id_capacitacion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150, verbose_name="Nombre")
    descripcion = models.CharField(max_length=300, blank=True, null=True, verbose_name="Descripción")
    organismo = models.CharField(max_length=150, blank=True, null=True, verbose_name="Organismo")
    estado = models.CharField(max_length=20, default='ACTIVO', verbose_name="Estado")

    class Meta:
        verbose_name = "Capacitación"
        verbose_name_plural = "Capacitaciones"

    def __str__(self):
        return self.nombre

class Feriante(models.Model):
    id_feriante = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nombre")
    apellido = models.CharField(max_length=100, blank=True, null=True, verbose_name="Apellido")
    dni = models.CharField(max_length=15, unique=True, verbose_name="DNI")
    sexo = models.CharField(max_length=10, blank=True, null=True, verbose_name="Sexo")
    mail = models.EmailField(max_length=150, blank=True, null=True, verbose_name="Correo Electrónico")
    telefono = models.CharField(max_length=30, blank=True, null=True, verbose_name="Teléfono")
    localidad = models.ForeignKey(Localidad, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Localidad")
    direccion = models.CharField(max_length=150, blank=True, null=True, verbose_name="Dirección")
    red_social = models.CharField(max_length=150, blank=True, null=True, verbose_name="Red Social")
    nombre_emprendimiento = models.CharField(max_length=150, blank=True, null=True, verbose_name="Nombre Emprendimiento")
    TIPO_ELABORACION_CHOICES = [
        ('Artesanal', 'Artesanal'),
        ('Reventa', 'Reventa'),
        ('Mixto', 'Mixto'),
    ]
    tipo_elaboracion = models.CharField(max_length=50, choices=TIPO_ELABORACION_CHOICES, blank=True, null=True, verbose_name="Tipo de Elaboración")
    observaciones = models.TextField(max_length=500, blank=True, null=True, verbose_name="Observaciones")
    estado = models.CharField(max_length=20, default='ACTIVO', verbose_name="Estado")
    fecha_alta = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Alta")
    foto = models.ImageField(upload_to='ferias/feriantes/', blank=True, null=True, verbose_name="Foto del Feriante")
    
    rubro = models.ForeignKey(RubroFeriante, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Rubro", related_name='feriantes_fk')
    subrubro = models.ForeignKey(SubrubroFeriante, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Subrubro")
    rubros = models.ManyToManyField(RubroFeriante, blank=True, verbose_name="Rubros")
    capacitaciones = models.ManyToManyField(CapacitacionFeriante, blank=True, verbose_name="Capacitaciones Realizadas")
    vecino_titular = models.ForeignKey('portal.Vecino', on_delete=models.SET_NULL, null=True, blank=True, related_name='perfil_feriante', verbose_name="Vecino Titular")

    class Meta:
        verbose_name = "Feriante"
        verbose_name_plural = "Feriantes"
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.apellido}, {self.nombre} ({self.dni})"

