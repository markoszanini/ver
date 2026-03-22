from django.db import models
from portal.models import Vecino
from datetime import date
from decimal import Decimal

class PartidaInmobiliaria(models.Model):
    nomenclatura = models.CharField(max_length=50, unique=True, verbose_name="Nomenclatura Catastral")
    direccion = models.CharField(max_length=200, verbose_name="Dirección")
    vecino = models.ForeignKey(Vecino, on_delete=models.SET_NULL, null=True, blank=True, related_name='partidas')

    class Meta:
        verbose_name = "Partida Inmobiliaria"
        verbose_name_plural = "Partidas Inmobiliarias"

    def __str__(self):
        return f"{self.nomenclatura} - {self.direccion}"

class Impuesto(models.Model):
    TIPO_CHOICES = [
        ('TGI', 'Tasa General de Inmuebles'),
        ('MUNICIPAL', 'Impuesto Municipal'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    vecino = models.ForeignKey(Vecino, on_delete=models.CASCADE, related_name='impuestos', null=True, blank=True)
    partida = models.ForeignKey(PartidaInmobiliaria, on_delete=models.CASCADE, related_name='impuestos', null=True, blank=True)

    class Meta:
        verbose_name = "Impuesto"
        verbose_name_plural = "Impuestos"

    def __str__(self):
        if self.tipo == 'TGI' and self.partida:
            return f"TGI - {self.partida.nomenclatura}"
        vecino_str = getattr(getattr(self, 'vecino', ''), 'user', 'Sin Vecino')
        return f"{self.get_tipo_display()} - {vecino_str}"

class Deuda(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
    ]
    impuesto = models.ForeignKey(Impuesto, on_delete=models.CASCADE, related_name='deudas')
    periodo = models.CharField(max_length=20, help_text="Ej: Enero 2026")
    monto_original = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_vencimiento = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    fecha_pago = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Deuda"
        verbose_name_plural = "Deudas"
        ordering = ['-fecha_vencimiento']

    def __str__(self):
        return f"{self.impuesto} - {self.periodo} ({self.estado})"

    @property
    def monto_actualizado(self):
        if self.estado == 'PAGADO':
            return self.monto_original
        hoy = date.today()
        if hoy > self.fecha_vencimiento:
            meses_atraso = (hoy.year - self.fecha_vencimiento.year) * 12 + hoy.month - self.fecha_vencimiento.month
            if meses_atraso > 0:
                interes = Decimal('0.03') * meses_atraso
                return round(self.monto_original * (Decimal('1') + interes), 2)
        return self.monto_original
