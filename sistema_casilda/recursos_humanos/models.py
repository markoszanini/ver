from django.db import models
from django.contrib.auth.models import User
from organigrama.models import Funcionario

class ReciboSueldo(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='recibos', verbose_name="Empleado")
    archivo = models.FileField(upload_to='recibos/%Y/%m/', verbose_name="Archivo PDF")
    mes = models.IntegerField(choices=[(i, str(i)) for i in range(1, 13)], verbose_name="Mes")
    anio = models.IntegerField(default=2026, verbose_name="Año")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Recibo de Sueldo"
        verbose_name_plural = "Recibos de Sueldo"
        ordering = ['-anio', '-mes']

    def __str__(self):
        return f"Recibo {self.mes}/{self.anio} - {self.funcionario.usuario_login}"

class Vacaciones(models.Model):
    funcionario = models.OneToOneField(Funcionario, on_delete=models.CASCADE, related_name='vacaciones', verbose_name="Empleado")
    anio_correspondiente = models.IntegerField(default=2025, verbose_name="Año Correspondiente")
    dias_totales = models.IntegerField(default=14, verbose_name="Días Totales")
    dias_tomados = models.IntegerField(default=0, verbose_name="Días Tomados")
    
    @property
    def dias_disponibles(self):
        return self.dias_totales - self.dias_tomados

    class Meta:
        verbose_name = "Vacaciones"
        verbose_name_plural = "Control de Vacaciones"

    def __str__(self):
        return f"Vacaciones {self.funcionario.usuario_login}"

class NovedadRRHH(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    mensaje = models.TextField(verbose_name="Mensaje")
    fecha = models.DateTimeField(auto_now_add=True)
    es_general = models.BooleanField(default=True, verbose_name="¿Es para todos?")
    funcionario_destino = models.ForeignKey(Funcionario, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Empleado Específico")

    class Meta:
        verbose_name = "Novedad de RRHH"
        verbose_name_plural = "Novedades de RRHH"
        ordering = ['-fecha']

    def __str__(self):
        return self.titulo
