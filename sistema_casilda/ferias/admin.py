from django.contrib import admin
from .models import RubroFeriante, SubrubroFeriante, CapacitacionFeriante, Feriante, Feria, InscripcionFeria
from portal.models import Notificacion, Vecino

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

class InscripcionFeriaInline(admin.TabularInline):
    model = InscripcionFeria
    extra = 0
    readonly_fields = ('fecha_inscripcion',)

@admin.register(Feria)
class FeriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha', 'horario', 'lugar', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('nombre', 'lugar')
    inlines = [InscripcionFeriaInline]

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        
        if is_new:
            # Notificar a todos los feriantes activos
            feriantes = Feriante.objects.filter(estado='ACTIVO', vecino_titular__isnull=False)
            notificaciones = []
            for f in feriantes:
                notificaciones.append(Notificacion(
                    vecino=f.vecino_titular,
                    titulo=f"Nueva Feria: {obj.nombre}",
                    mensaje=f"Se ha programado una nueva feria para el día {obj.fecha} en {obj.lugar}. ¡Inscribite ahora!",
                    link="/ferias/mis-ferias/" # Suponiendo que esta será la ruta
                ))
            if notificaciones:
                Notificacion.objects.bulk_create(notificaciones)

@admin.register(InscripcionFeria)
class InscripcionFeriaAdmin(admin.ModelAdmin):
    list_display = ('feriante', 'feria', 'fecha_inscripcion', 'estado')
    list_filter = ('estado', 'feria')
    search_fields = ('feriante__apellido', 'feriante__nombre', 'feria__nombre')

@admin.register(Feriante)
class FerianteAdmin(admin.ModelAdmin):
    list_display = ('apellido', 'nombre', 'dni', 'rubro', 'subrubro', 'estado', 'fecha_alta')
    search_fields = ('apellido', 'nombre', 'dni', 'nombre_emprendimiento')
    list_filter = ('estado', 'localidad', 'rubro')
    filter_horizontal = ('capacitaciones',)
    readonly_fields = ('fecha_alta',)
    
    fieldsets = (
        ('Datos Personales', {
            'fields': (
                ('nombre', 'apellido'),
                ('dni', 'sexo'),
                ('mail', 'telefono'),
                ('localidad', 'calle', 'altura'),
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
