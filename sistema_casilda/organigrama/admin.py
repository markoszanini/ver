from django.contrib import admin
from .models import Area, Direccion, Departamento, Division, Subdivision, Seccion, Oficina
from .forms import FuncionarioForm

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'area')
    list_filter = ('area',)

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'area', 'direccion')
    list_filter = ('area', 'direccion')

admin.site.register(Division)
admin.site.register(Subdivision)
admin.site.register(Seccion)
admin.site.register(Oficina)
