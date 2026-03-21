from django.contrib import admin
from .models import Expediente, MovimientoExpediente

@admin.register(Expediente)
class ExpedienteAdmin(admin.ModelAdmin):
    list_display = ('nro_expediente', 'asunto', 'fecha_ingreso', 'estado', 'destino')
    search_fields = ('nro_expediente', 'asunto', 'origen_interno')
    list_filter = ('estado', 'tipo_expediente', 'fecha_ingreso')

@admin.register(MovimientoExpediente)
class MovimientoExpedienteAdmin(admin.ModelAdmin):
    list_display = ('expediente', 'fecha_ingreso', 'procedencia', 'destino', 'estado')
    search_fields = ('expediente__nro_expediente',)
    list_filter = ('estado', 'fecha_ingreso')
