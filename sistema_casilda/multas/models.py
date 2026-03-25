from django.db import models
from django.utils import timezone
from portal.models import Localidad

class Persona(models.Model):
    id_persona = models.AutoField(primary_key=True)
    dni = models.CharField(max_length=20, unique=True, verbose_name="DNI")
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    localidad = models.ForeignKey(Localidad, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Localidad")
    calle = models.CharField(max_length=100, null=True, blank=True)
    numero = models.CharField(max_length=10, null=True, blank=True)
    codigo_postal = models.CharField(max_length=10, null=True, blank=True)
    telefono = models.CharField(max_length=30, null=True, blank=True)
    correo = models.EmailField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'PERSONAS'
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'

    def __str__(self):
        return f"{self.apellido}, {self.nombre} (DNI: {self.dni})"


class Vehiculo(models.Model):
    id_vehiculo = models.AutoField(primary_key=True)
    patente = models.CharField(max_length=20, unique=True)
    marca = models.CharField(max_length=50, null=True, blank=True)
    modelo = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=30, null=True, blank=True)
    tipo_vehiculo = models.CharField(max_length=50, null=True, blank=True)
    categoria = models.CharField(max_length=50, null=True, blank=True)
    anio_fabricacion = models.IntegerField(null=True, blank=True, verbose_name="Año Fabricación")
    titular = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True, blank=True, db_column='ID_TITULAR', related_name='vehiculos')

    class Meta:
        db_table = 'VEHICULOS'
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'

    def __str__(self):
        return f"{self.patente} - {self.marca} {self.modelo}"


class Inmueble(models.Model):
    id_inmueble = models.AutoField(primary_key=True)
    nomenclatura = models.CharField(max_length=50, unique=True)
    cuil = models.CharField(max_length=20, null=True, blank=True)
    razon_social = models.CharField(max_length=100, null=True, blank=True)
    calle = models.CharField(max_length=100, null=True, blank=True)
    numero = models.CharField(max_length=10, null=True, blank=True)
    manzana = models.CharField(max_length=10, null=True, blank=True)
    seccion = models.CharField(max_length=10, null=True, blank=True)
    parcela = models.CharField(max_length=10, null=True, blank=True)
    tipo_inmueble = models.CharField(max_length=50, null=True, blank=True)
    uso_inmueble = models.CharField(max_length=50, null=True, blank=True)
    metros_cuadrados = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'INMUEBLES'
        verbose_name = 'Inmueble'
        verbose_name_plural = 'Inmuebles'

    def __str__(self):
        return f"{self.nomenclatura} - {self.calle} {self.numero}"


class Animal(models.Model):
    id_animal = models.AutoField(primary_key=True)
    raza = models.CharField(max_length=50, null=True, blank=True)
    especie = models.CharField(max_length=50, null=True, blank=True)
    SEXO_CHOICES = [
        ('Femenino', 'Femenino'),
        ('Masculino', 'Masculino'),
        ('Otro', 'Otro'),
    ]
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES, null=True, blank=True)
    propietario = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True, blank=True, db_column='ID_PROPIETARIO', related_name='animales')

    class Meta:
        db_table = 'ANIMALES'
        verbose_name = 'Animal'
        verbose_name_plural = 'Animales'

    def __str__(self):
        return f"{self.especie} ({self.raza})"


class Inspector(models.Model):
    id_inspector = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    departamento = models.CharField(max_length=50, null=True, blank=True)
    cargo = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'INSPECTORES'
        verbose_name = 'Inspector'
        verbose_name_plural = 'Inspectores'

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"


class Motivo(models.Model):
    id_motivo = models.AutoField(primary_key=True)
    tipo_acta = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)

    class Meta:
        db_table = 'MOTIVOS'
        verbose_name = 'Motivo de Infracción'
        verbose_name_plural = 'Motivos de Infracción'

    def __str__(self):
        return f"[{self.tipo_acta}] {self.descripcion}"


class Acta(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADA', 'Pagada'),
        ('ANULADA', 'Anulada'),
        ('CADUCA', 'Caduca'),
    ]

    id_acta = models.AutoField(primary_key=True)
    persona = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True, blank=True, db_column='ID_PERSONA', related_name='actas')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.SET_NULL, null=True, blank=True, db_column='ID_VEHICULO', related_name='actas')
    inmueble = models.ForeignKey(Inmueble, on_delete=models.SET_NULL, null=True, blank=True, db_column='ID_INMUEBLE', related_name='actas')
    TIPO_ACTA_CHOICES = [
        ('ANIMAL', 'Animal'),
        ('VEHICULO', 'Vehículo'),
        ('INMUEBLE', 'Inmueble'),
    ]
    animal = models.ForeignKey(Animal, on_delete=models.SET_NULL, null=True, blank=True, db_column='ID_ANIMAL', related_name='actas')
    tipo_acta = models.CharField(max_length=50, choices=TIPO_ACTA_CHOICES)
    motivo = models.ForeignKey(Motivo, on_delete=models.SET_NULL, null=True, blank=True, db_column='ID_MOTIVO')
    inspector = models.ForeignKey(Inspector, on_delete=models.SET_NULL, null=True, blank=True, db_column='ID_INSPECTOR')
    fecha_infraccion = models.DateField(default=timezone.now)
    lugar_infraccion = models.CharField(max_length=200, null=True, blank=True)
    descripcion = models.TextField(max_length=500, null=True, blank=True)
    uf = models.CharField(max_length=50, null=True, blank=True, verbose_name="Unidades Fijas (UF)")
    foto_infraccion = models.ImageField(upload_to='multas/fotos/', null=True, blank=True)
    importe = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    numero_acta = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'ACTAS'
        verbose_name = 'Acta de Infracción'
        verbose_name_plural = 'Actas de Infracción'

    def __str__(self):
        return f"Acta N° {self.numero_acta} - {self.estado}"


class Documentacion(models.Model):
    id_doc = models.AutoField(primary_key=True)
    tipo_doc = models.CharField(max_length=50, null=True, blank=True)
    acta = models.ForeignKey(Acta, on_delete=models.CASCADE, null=True, blank=True, db_column='ID_ACTA', related_name='documentos')
    fecha_generacion = models.DateField(default=timezone.now)
    usuario_genera = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'DOCUMENTACION'
        verbose_name = 'Documentación'
        verbose_name_plural = 'Documentaciones'

    def __str__(self):
        return f"{self.tipo_doc} - Acta {self.acta_id if self.acta else ''}"
