from django.db import models
from portal.models import Vecino
from organigrama.models import Area, Direccion, Departamento, Division, Subdivision, Seccion, Oficina

class Expediente(models.Model):
    id_expediente = models.AutoField(primary_key=True)
    nro_expediente = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="Número de Expediente")
    fecha_ingreso = models.DateField(verbose_name="Fecha de Ingreso", auto_now_add=True)
    
    # Origen (quién lo inició)
    origen_area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes_creados')
    origen_direccion = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes_creados')
    origen_departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes_creados')
    origen_oficina = models.ForeignKey(Oficina, on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes_creados')
    
    asunto = models.TextField(max_length=2000, blank=True, null=True, verbose_name="Asunto")
    
    # Ubicación Actual (dónde está ahora)
    actual_area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes_actuales')
    actual_direccion = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes_actuales')
    actual_departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes_actuales')
    actual_oficina = models.ForeignKey(Oficina, on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes_actuales')

    fecha_salida = models.DateField(blank=True, null=True, verbose_name="Fecha de Finalización")
    estado = models.CharField(max_length=50, default='En trámite', verbose_name="Estado")
    observaciones = models.TextField(max_length=2000, blank=True, null=True, verbose_name="Observaciones")
    registrado_por = models.CharField(max_length=100, blank=True, null=True, verbose_name="Registrado por (Mesa Entrada)")
    foto = models.ImageField(upload_to='expedientes/fotos/', blank=True, null=True, verbose_name="Documento/Foto")
    
    # Opcional: Si el origen fue un vecino
    vecino_titular = models.ForeignKey(Vecino, on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes', verbose_name="Vecino Titular")
    class Meta:
        verbose_name = "Expediente"
        verbose_name_plural = "Expedientes"
        ordering = ['-fecha_ingreso', '-id_expediente']

    def __str__(self):
        return f"{self.nro_expediente} - {self.asunto}"

class MovimientoExpediente(models.Model):
    id_movimiento = models.AutoField(primary_key=True)
    expediente = models.ForeignKey(Expediente, on_delete=models.CASCADE, related_name='movimientos')
    fecha_pase = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del Pase")
    
    # Destino del Pase
    destino_area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)
    destino_direccion = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True, blank=True)
    destino_departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True)
    destino_oficina = models.ForeignKey(Oficina, on_delete=models.SET_NULL, null=True, blank=True)
    
    estado = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nuevo Estado")
    observacion = models.TextField(max_length=2000, blank=True, null=True, verbose_name="Nota de Pase")
    usuario_emisor = models.CharField(max_length=100, blank=True, null=True, verbose_name="Enviado por")

    class Meta:
        verbose_name = "Pase de Expediente"
        verbose_name_plural = "Historial de Pases"
        ordering = ['-fecha_pase']

    def __str__(self):
        return f"Pase de {self.expediente.nro_expediente} emitido el {self.fecha_pase.strftime('%d/%m/%Y %H:%M')}"
