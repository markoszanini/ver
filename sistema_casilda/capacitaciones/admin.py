from django.contrib import admin
from django.contrib import messages
from .models import Capacitacion, Inscripcion

@admin.register(Capacitacion)
class CapacitacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'area_responsable', 'fecha_inicio', 'cupo_maximo', 'estado_inscripcion')
    list_filter = ('area_responsable', 'estado_inscripcion')
    search_fields = ('nombre',)
    exclude = ('area_responsable',)
    actions = ['abrir_inscripcion', 'cerrar_inscripcion']

    def save_model(self, request, obj, form, change):
        if not getattr(obj, 'area_responsable', None):
            funcionario = getattr(request.user, 'funcionario_link', None)
            if funcionario:
                nombre_area = funcionario.area.nombre.lower() if funcionario.area else ""
                nombre_depto = funcionario.departamento.nombre.lower() if funcionario.departamento else ""
                nombre_oficina = funcionario.oficina.nombre.lower() if funcionario.oficina else ""
                nombre_dir = funcionario.direccion.nombre.lower() if funcionario.direccion else ""
                
                if 'seguridad alimentaria' in nombre_depto:
                    obj.area_responsable = 'ASAC'
                elif 'producc' in nombre_area:
                    obj.area_responsable = 'PRODUCCION'
                elif 'quinquela' in nombre_oficina or 'cultura' in nombre_dir:
                    obj.area_responsable = 'QUINQUELA'
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
            
        funcionario = getattr(request.user, 'funcionario_link', None)
        if funcionario:
            nombre_area = funcionario.area.nombre.lower() if funcionario.area else ""
            nombre_depto = funcionario.departamento.nombre.lower() if funcionario.departamento else ""
            nombre_oficina = funcionario.oficina.nombre.lower() if funcionario.oficina else ""
            nombre_dir = funcionario.direccion.nombre.lower() if funcionario.direccion else ""
            
            allowed_areas = []
            if 'seguridad alimentaria' in nombre_depto:
                allowed_areas.append('ASAC')
            if 'producc' in nombre_area:
                allowed_areas.append('PRODUCCION')
            if 'quinquela' in nombre_oficina or 'cultura' in nombre_dir:
                allowed_areas.append('QUINQUELA')
                
            return qs.filter(area_responsable__in=allowed_areas)
        return qs.none()

    @admin.action(description="Abrir inscripción masivamente")
    def abrir_inscripcion(self, request, queryset):
        queryset.update(estado_inscripcion='ABIERTA')
        self.message_user(request, "Inscripciones abiertas correctamente.")

    @admin.action(description="Cerrar inscripción masivamente")
    def cerrar_inscripcion(self, request, queryset):
        queryset.update(estado_inscripcion='CERRADA')
        self.message_user(request, "Inscripciones cerradas correctamente.")

@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('capacitacion', 'vecino', 'fecha_inscripcion', 'estado')
    list_filter = ('estado', 'capacitacion__area_responsable')
    search_fields = ('vecino__user__first_name', 'vecino__user__last_name', 'vecino__user__username', 'capacitacion__nombre')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
            
        funcionario = getattr(request.user, 'funcionario_link', None)
        if funcionario:
            nombre_area = funcionario.area.nombre.lower() if funcionario.area else ""
            nombre_depto = funcionario.departamento.nombre.lower() if funcionario.departamento else ""
            nombre_oficina = funcionario.oficina.nombre.lower() if funcionario.oficina else ""
            nombre_dir = funcionario.direccion.nombre.lower() if funcionario.direccion else ""
            
            allowed_areas = []
            if 'seguridad alimentaria' in nombre_depto:
                allowed_areas.append('ASAC')
            if 'producc' in nombre_area:
                allowed_areas.append('PRODUCCION')
            if 'quinquela' in nombre_oficina or 'cultura' in nombre_dir:
                allowed_areas.append('QUINQUELA')
                
            return qs.filter(capacitacion__area_responsable__in=allowed_areas)
        return qs.none()
