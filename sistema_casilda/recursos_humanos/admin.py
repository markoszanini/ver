from django.contrib import admin
from .models import ReciboSueldo, Vacaciones, NovedadRRHH

@admin.register(ReciboSueldo)
class ReciboSueldoAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'mes', 'anio', 'fecha_subida')
    list_filter = ('anio', 'mes', 'funcionario')
    search_fields = ('funcionario__usuario_login', 'funcionario__nombre', 'funcionario__apellido')

@admin.register(Vacaciones)
class VacacionesAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'anio_correspondiente', 'dias_totales', 'dias_tomados', 'dias_disponibles')
    search_fields = ('funcionario__usuario_login',)

@admin.register(NovedadRRHH)
class NovedadRRHHAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha', 'es_general', 'funcionario_destino')
    list_filter = ('es_general', 'fecha')
    search_fields = ('titulo', 'mensaje')
