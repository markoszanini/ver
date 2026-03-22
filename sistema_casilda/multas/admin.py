from django.contrib import admin
from .models import Persona, Vehiculo, Inmueble, Animal, Inspector, Motivo, Acta, Documentacion

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('dni', 'apellido', 'nombre', 'localidad')
    search_fields = ('dni', 'apellido', 'nombre')

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('patente', 'marca', 'modelo', 'titular')
    search_fields = ('patente', 'marca', 'titular__dni')

@admin.register(Inmueble)
class InmuebleAdmin(admin.ModelAdmin):
    list_display = ('nomenclatura', 'calle', 'numero', 'razon_social')
    search_fields = ('nomenclatura', 'calle', 'cuil')

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('especie', 'raza', 'sexo', 'propietario')
    search_fields = ('especie', 'raza', 'propietario__dni')

@admin.register(Inspector)
class InspectorAdmin(admin.ModelAdmin):
    list_display = ('apellido', 'nombre', 'cargo')
    search_fields = ('apellido', 'nombre')

@admin.register(Motivo)
class MotivoAdmin(admin.ModelAdmin):
    list_display = ('tipo_acta', 'descripcion')
    list_filter = ('tipo_acta',)
    search_fields = ('descripcion',)

class DocumentacionInline(admin.TabularInline):
    model = Documentacion
    extra = 1

from .forms import ActaAdminForm

@admin.register(Acta)
class ActaAdmin(admin.ModelAdmin):
    form = ActaAdminForm
    
    class Media:
        js = ('js/multas_admin.js',)
        css = {
             'all': ('css/multas_admin.css',)
        }

    list_display = ('numero_acta', 'tipo_acta', 'fecha_infraccion', 'estado', 'importe', 'uf', 'motivo')
    list_filter = ('estado', 'tipo_acta', 'fecha_infraccion')
    search_fields = ('numero_acta', 'persona__dni', 'vehiculo__patente', 'inmueble__nomenclatura')
    inlines = [DocumentacionInline]
    
    exclude = ('persona', 'vehiculo', 'animal', 'inmueble')

    def get_fieldsets(self, request, obj=None):
        resolucion_fields = ('motivo', 'importe', 'uf')
        if obj: # Si es edición, se permite ver el estado
            resolucion_fields = ('estado', 'motivo', 'importe', 'uf')

        return (
            ('Acta de Infracción', {
                'fields': (
                    ('numero_acta', 'fecha_infraccion'),
                    'tipo_acta',
                    ('inspector', 'lugar_infraccion'),
                    'descripcion',
                    'foto_infraccion',
                )
            }),
            ('Resolución de Infracción', {
                'fields': resolucion_fields
            }),
            ('Datos Personales', {
                'classes': ('fieldset-persona',),
                'fields': (
                    ('pers_dni',),
                    ('pers_apellido', 'pers_nombre', 'pers_fecha_nacimiento'),
                    ('pers_calle', 'pers_numero', 'pers_codigo_postal', 'pers_localidad'),
                    ('pers_telefono', 'pers_correo'),
                )
            }),
            ('Datos del Vehículo', {
                'classes': ('fieldset-vehiculo',),
                'fields': (
                    ('veh_patente',),
                    ('veh_marca', 'veh_modelo', 'veh_color'),
                    ('veh_tipo_vehiculo', 'veh_categoria', 'veh_anio_fabricacion'),
                )
            }),
            ('Datos del Inmueble', {
                'classes': ('fieldset-inmueble',),
                'fields': (
                    ('inm_nomenclatura', 'inm_cuil', 'inm_razon_social'),
                    ('inm_calle', 'inm_numero', 'inm_manzana', 'inm_seccion', 'inm_parcela'),
                    ('inm_tipo_inmueble', 'inm_uso_inmueble', 'inm_metros_cuadrados'),
                )
            }),
            ('Datos del Animal', {
                'classes': ('fieldset-animal',),
                'fields': (
                    ('ani_especie', 'ani_raza', 'ani_sexo'),
                )
            }),
        )

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            all_fields = [f.name for f in self.model._meta.fields if f.name not in ['id_acta']]
            allowed_fields = ['importe', 'uf', 'estado']
            return [f for f in all_fields if f not in allowed_fields]
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        dni = form.cleaned_data.get('pers_dni')
        persona = None
        if dni:
            persona, _ = Persona.objects.update_or_create(
                dni=dni,
                defaults={
                    'nombre': form.cleaned_data.get('pers_nombre'),
                    'apellido': form.cleaned_data.get('pers_apellido'),
                    'fecha_nacimiento': form.cleaned_data.get('pers_fecha_nacimiento'),
                    'localidad': form.cleaned_data.get('pers_localidad'),
                    'calle': form.cleaned_data.get('pers_calle'),
                    'numero': form.cleaned_data.get('pers_numero'),
                    'codigo_postal': form.cleaned_data.get('pers_codigo_postal'),
                    'telefono': form.cleaned_data.get('pers_telefono'),
                    'correo': form.cleaned_data.get('pers_correo'),
                }
            )
            obj.persona = persona
        
        tipo_acta = form.cleaned_data.get('tipo_acta') or obj.tipo_acta
        
        if tipo_acta == 'VEHICULO':
            patente = form.cleaned_data.get('veh_patente')
            if patente:
                vehiculo, _ = Vehiculo.objects.update_or_create(
                    patente=patente,
                    defaults={
                        'marca': form.cleaned_data.get('veh_marca'),
                        'modelo': form.cleaned_data.get('veh_modelo'),
                        'color': form.cleaned_data.get('veh_color'),
                        'tipo_vehiculo': form.cleaned_data.get('veh_tipo_vehiculo'),
                        'categoria': form.cleaned_data.get('veh_categoria'),
                        'anio_fabricacion': form.cleaned_data.get('veh_anio_fabricacion'),
                        'titular': persona,
                    }
                )
                obj.vehiculo = vehiculo
                obj.animal = None
                obj.inmueble = None
        elif tipo_acta == 'ANIMAL':
            if obj.animal_id:
                animal = obj.animal
                animal.raza = form.cleaned_data.get('ani_raza')
                animal.especie = form.cleaned_data.get('ani_especie')
                animal.sexo = form.cleaned_data.get('ani_sexo')
                animal.propietario = persona
                animal.save()
            else:
                animal = Animal.objects.create(
                    raza=form.cleaned_data.get('ani_raza'),
                    especie=form.cleaned_data.get('ani_especie'),
                    sexo=form.cleaned_data.get('ani_sexo'),
                    propietario=persona
                )
            obj.animal = animal
            obj.vehiculo = None
            obj.inmueble = None
        elif tipo_acta == 'INMUEBLE':
            nomenc = form.cleaned_data.get('inm_nomenclatura')
            if nomenc:
                inmueble, _ = Inmueble.objects.update_or_create(
                    nomenclatura=nomenc,
                    defaults={
                        'cuil': form.cleaned_data.get('inm_cuil'),
                        'razon_social': form.cleaned_data.get('inm_razon_social'),
                        'calle': form.cleaned_data.get('inm_calle'),
                        'numero': form.cleaned_data.get('inm_numero'),
                        'manzana': form.cleaned_data.get('inm_manzana'),
                        'seccion': form.cleaned_data.get('inm_seccion'),
                        'parcela': form.cleaned_data.get('inm_parcela'),
                        'tipo_inmueble': form.cleaned_data.get('inm_tipo_inmueble'),
                        'uso_inmueble': form.cleaned_data.get('inm_uso_inmueble'),
                        'metros_cuadrados': form.cleaned_data.get('inm_metros_cuadrados'),
                    }
                )
                obj.inmueble = inmueble
                obj.vehiculo = None
                obj.animal = None
        
        super().save_model(request, obj, form, change)

@admin.register(Documentacion)
class DocumentacionAdmin(admin.ModelAdmin):
    list_display = ('tipo_doc', 'acta', 'fecha_generacion', 'usuario_genera')
    search_fields = ('tipo_doc', 'acta__numero_acta')
