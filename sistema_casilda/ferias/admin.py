from django.contrib import admin
from .models import RubroFeriante, SubrubroFeriante, CapacitacionFeriante, Feriante

@admin.register(RubroFeriante)
class RubroFerianteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'estado')
    def has_module_permission(self, request):
        return False

@admin.register(SubrubroFeriante)
class SubrubroFerianteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rubro')
    list_filter = ('rubro',)
    def has_module_permission(self, request):
        return False

@admin.register(CapacitacionFeriante)
class CapacitacionFerianteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'organismo', 'estado')
    def has_module_permission(self, request):
        return False

@admin.register(Feriante)
class FerianteAdmin(admin.ModelAdmin):
    list_display = ('apellido', 'nombre', 'dni', 'rubro', 'subrubro', 'estado', 'fecha_alta')
    search_fields = ('apellido', 'nombre', 'dni', 'nombre_emprendimiento')
    list_filter = ('estado', 'localidad', 'rubro')
    filter_horizontal = ('capacitaciones',)
    
    fieldsets = (
        ('Datos Personales', {
            'fields': (
                ('nombre', 'apellido'),
                ('dni', 'sexo'),
                ('mail', 'telefono'),
                ('localidad', 'direccion'),
                'red_social',
            )
        }),
        ('Emprendimiento', {
            'fields': (
                'nombre_emprendimiento',
                ('rubro', 'subrubro'),
                ('tipo_elaboracion', 'foto'),
            )
        }),
        ('Capacitaciones y Otros', {
            'fields': (
                'capacitaciones',
                'observaciones',
            )
        }),
        ('Estado de Registro', {
            'fields': (('estado', 'fecha_alta'),),
            'classes': ('collapse',),
        }),
    )

    class Media:
        js = ('js/chained_subrubro.js?v=2',)
        css = {
            'all': ('css/ferias_admin.css',)
        }
