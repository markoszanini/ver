from django.contrib import admin
from .models import Vecino, Notificacion

@admin.register(Vecino)
class VecinoAdmin(admin.ModelAdmin):
    list_display = ('user', 'dni', 'telefono', 'calle', 'altura')
    search_fields = ('dni', 'user__first_name', 'user__last_name')

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('vecino', 'titulo', 'fecha', 'leida')
    list_filter = ('leida', 'fecha')
    search_fields = ('vecino__dni', 'titulo')
