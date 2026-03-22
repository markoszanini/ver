from django.contrib import admin
from .models import Funcionario, Area, Direccion, Departamento, Division, Subdivision, Seccion, Oficina
from .forms import FuncionarioForm

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    form = FuncionarioForm
    list_display = ('usuario_login', 'nombre', 'apellido', 'activo', 'rango', 'area')
    search_fields = ('usuario_login', 'nombre', 'apellido', 'email')
    list_filter = ('activo', 'rango', 'area', 'departamento')

    fieldsets = (
        ('Datos Personales y Credenciales', {
            'classes': ('tab-datos',),
            'fields': (
                ('usuario_login', 'activo', 'id_empleado_externo'),
                ('nombre', 'apellido', 'email'),
                'password_nueva', 
            )
        }),
        ('Lugar de Trabajo', {
            'classes': ('tab-lugar',),
            'fields': (
                'area',
                'direccion',
                'departamento',
                'division',
                'subdivision',
                'seccion',
                'oficina'
            )
        }),
        ('Rol Asignado', {
            'classes': ('tab-rol',),
            'fields': ('rango',)
        }),
    )

    class Media:
        js = ('js/organigrama_admin.js',)
        css = {'all': ('css/multas_admin.css',)}  # reutilizamos las cajas select2 ensanchadas

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
