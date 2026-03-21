from django.contrib import admin
from django import forms
from .models import (RubroEmpleo, PuestoEmpleo, Postulante, Curso, Experiencia, Estudio, Idioma, Postulacion)

class ExperienciaForm(forms.ModelForm):
    class Meta:
        model = Experiencia
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'puesto' in self.fields:
            self.fields['puesto'].queryset = PuestoEmpleo.objects.none()
            if 'rubro' in self.data:
                try:
                    rubro_id = int(self.data.get('rubro'))
                    self.fields['puesto'].queryset = PuestoEmpleo.objects.filter(rubro_id=rubro_id).order_by('descripcion')
                except (ValueError, TypeError):
                    pass
            elif self.instance.pk and self.instance.rubro:
                self.fields['puesto'].queryset = PuestoEmpleo.objects.filter(rubro=self.instance.rubro).order_by('descripcion')

class PostulacionForm(forms.ModelForm):
    class Meta:
        model = Postulacion
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'puesto' in self.fields:
            self.fields['puesto'].queryset = PuestoEmpleo.objects.none()
            if 'rubro' in self.data:
                try:
                    rubro_id = int(self.data.get('rubro'))
                    self.fields['puesto'].queryset = PuestoEmpleo.objects.filter(rubro_id=rubro_id).order_by('descripcion')
                except (ValueError, TypeError):
                    pass
            elif self.instance.pk and self.instance.rubro:
                self.fields['puesto'].queryset = PuestoEmpleo.objects.filter(rubro=self.instance.rubro).order_by('descripcion')

class CursoInline(admin.TabularInline): model = Curso; extra = 1

class ExperienciaInline(admin.StackedInline): 
    model = Experiencia
    extra = 1
    form = ExperienciaForm
    fields = ('rubro', 'puesto', 'empresa', 'fecha_desde', 'fecha_hasta', 'descripcion')

class EstudioInline(admin.TabularInline): model = Estudio; extra = 1
class IdiomaInline(admin.TabularInline): model = Idioma; extra = 1

class PostulacionInline(admin.TabularInline):
    model = Postulacion
    extra = 1
    form = PostulacionForm
    fields = ('rubro', 'puesto', 'orden')

@admin.register(Postulante)
class PostulanteAdmin(admin.ModelAdmin):
    list_display = ('get_dni', 'apellido', 'nombre', 'localidad', 'situacion_actual', 'estado')
    search_fields = ('apellido', 'nombre', 'mail', 'vecino__dni')
    list_filter = ('estado', 'localidad')
    exclude = ('estado', 'puestos')

    def get_dni(self, obj):
        return obj.vecino.dni if obj.vecino else '-'
    get_dni.short_description = 'DNI'
    inlines = [PostulacionInline, ExperienciaInline, EstudioInline, CursoInline, IdiomaInline]

    fieldsets = (
        ('Datos Personales', {
            'fields': (
                ('nombre', 'apellido'),
                ('fecha_nac', 'sexo'),
                ('domicilio', 'localidad'),
                ('localidad_detalle', 'cp'),
                ('telefono', 'mail'),
                'situacion_actual',
                ('sobre_mi', 'cv'),
            )
        }),
        ('Movilidad y Disponibilidad', {
            'fields': (
                ('movilidad_propia', 'medio_movilidad'),
                ('licencia_conducir', 'licencia_categoria'),
                'licencia_vencimiento',
                ('disponibilidad_viajar', 'disponibilidad_horaria'),
            )
        }),
    )

    class Media:
        js = ('js/chained_puesto.js?v=6',)
