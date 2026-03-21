from django.db import models
from django.utils import timezone

class OrdenCompra(models.Model):
    id_oc = models.AutoField(primary_key=True)
    nro_oc = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nro de orden")
    seccion_solicita = models.CharField(max_length=200, blank=True, null=True, verbose_name="Sección que solicita")
    fecha_solicitud = models.DateField(default=timezone.now, verbose_name="Fecha solicitud")
    destino = models.CharField(max_length=200, blank=True, null=True, verbose_name="Destino del pedido")
    observaciones = models.TextField(max_length=2000, blank=True, null=True, verbose_name="Observaciones")
    ESTADOS_OC = [
        ('En curso', 'En curso'),
        ('Finalizado', 'Finalizado'),
        ('Cancelado', 'Cancelado')
    ]
    estado = models.CharField(max_length=50, choices=ESTADOS_OC, default='En curso', verbose_name="Estado")
    registrado_por = models.CharField(max_length=100, blank=True, null=True, verbose_name="Solicitado por")
    archivo_orden = models.FileField(upload_to='compras/ordenes/', blank=True, null=True, verbose_name="Foto de la orden")
    fecha_entrega = models.DateField(blank=True, null=True, verbose_name="Fecha de entrega")
    quien_entrego = models.CharField(max_length=200, blank=True, null=True, verbose_name="Entrega realizada por")
    observacion_entrega = models.TextField(max_length=1000, blank=True, null=True, verbose_name="Observacion Entrega")
    origen_fondos = models.CharField(max_length=200, blank=True, null=True, verbose_name="Origen del fondo")

    class Meta:
        verbose_name = "Orden de Compra"
        verbose_name_plural = "Nueva Orden de Compra"
        ordering = ['-fecha_solicitud', '-id_oc']

    def __str__(self):
        return f"OC {self.nro_oc} - {self.seccion_solicita}"

class DetalleOrdenCompra(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    orden_compra = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE, related_name='detalles')
    item = models.PositiveIntegerField(verbose_name="Ítem", blank=True, null=True)
    descripcion = models.CharField(max_length=500, verbose_name="Detalle")
    cantidad_pedida = models.PositiveIntegerField(verbose_name="Cantidad")
    cantidad_recibida = models.PositiveIntegerField(default=0, verbose_name="Cantidad Recibida")
    fecha_recepcion = models.DateField(blank=True, null=True, verbose_name="Fecha de Recepción")
    recibido_por = models.CharField(max_length=100, blank=True, null=True, verbose_name="Recibido por")
    traido_por = models.CharField(max_length=100, blank=True, null=True, verbose_name="Traído por")
    observaciones = models.TextField(max_length=500, blank=True, null=True, verbose_name="Observaciones")
    estado = models.CharField(max_length=50, choices=OrdenCompra.ESTADOS_OC, default='En curso', verbose_name="Estado")

    class Meta:
        verbose_name = "Detalle de OC"
        verbose_name_plural = "Detalles de OC"
        ordering = ['orden_compra', 'item']

    def __str__(self):
        return f"Item {self.item} - {self.descripcion}"

class SeguimientoOC(OrdenCompra):
    class Meta:
        proxy = True
        verbose_name = "Seguimiento OC"
        verbose_name_plural = "Seguimiento OC"
