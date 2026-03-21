from django.contrib import admin
from .models import Vecino

@admin.register(Vecino)
class VecinoAdmin(admin.ModelAdmin):
    list_display = ('user', 'dni', 'telefono', 'domicilio')
    search_fields = ('dni', 'user__first_name', 'user__last_name')
