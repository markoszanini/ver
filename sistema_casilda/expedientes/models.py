from django.db import models

class Expediente(models.Model):
    id_expediente = models.AutoField(primary_key=True)
    nro_expediente = models.CharField(max_length=50, unique=True, verbose_name="Número de Expediente")
    fecha_ingreso = models.DateField(verbose_name="Fecha de Ingreso")
    procedencia = models.CharField(max_length=200, blank=True, null=True, verbose_name="Procedencia")
    asunto = models.TextField(max_length=2000, blank=True, null=True, verbose_name="Asunto")
    destino = models.CharField(max_length=200, blank=True, null=True, verbose_name="Destino")
    fecha_salida = models.DateField(blank=True, null=True, verbose_name="Fecha de Salida")
    estado = models.CharField(max_length=50, default='En trámite', verbose_name="Estado")
    observaciones = models.TextField(max_length=2000, blank=True, null=True, verbose_name="Observaciones")
    registrado_por = models.CharField(max_length=100, blank=True, null=True, verbose_name="Registrado por")
    foto = models.ImageField(upload_to='expedientes/fotos/', blank=True, null=True, verbose_name="Foto del Expediente")
    tipo_expediente = models.CharField(max_length=20, default='RECIBIDO', verbose_name="Tipo de Expediente")
    origen_interno = models.CharField(max_length=100, blank=True, null=True, verbose_name="Origen Interno")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    vecino_titular = models.ForeignKey('portal.Vecino', on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes', verbose_name="Vecino Titular")

    class Meta:
        verbose_name = "Expediente"
        verbose_name_plural = "Expedientes"
        ordering = ['-fecha_ingreso', '-id_expediente']

    def __str__(self):
        return f"{self.nro_expediente} - {self.asunto}"

class MovimientoExpediente(models.Model):
    id_movimiento = models.AutoField(primary_key=True)
    expediente = models.ForeignKey(Expediente, on_delete=models.CASCADE, related_name='movimientos')
    fecha_ingreso = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Ingreso")
    procedencia = models.CharField(max_length=200, blank=True, null=True, verbose_name="Procedencia")
    destino = models.CharField(max_length=200, blank=True, null=True, verbose_name="Destino")
    estado = models.CharField(max_length=50, blank=True, null=True, verbose_name="Estado")
    fecha_salida = models.DateField(blank=True, null=True, verbose_name="Fecha de Salida")
    observacion = models.TextField(max_length=2000, blank=True, null=True, verbose_name="Observación")
    foto = models.ImageField(upload_to='expedientes/movimientos/', blank=True, null=True, verbose_name="Foto del Movimiento")
    usuario = models.CharField(max_length=100, blank=True, null=True, verbose_name="Usuario")
    fecha_archivado = models.DateField(blank=True, null=True, verbose_name="Fecha de Archivado")

    class Meta:
        verbose_name = "Movimiento de Expediente"
        verbose_name_plural = "Movimientos de Expediente"
        ordering = ['-fecha_ingreso']

    def __str__(self):
        return f"Movimiento de {self.expediente.nro_expediente} a {self.destino}"
