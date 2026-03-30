from django.contrib import admin
from django.contrib import messages
from .models import Capacitacion, Inscripcion

@admin.register(Capacitacion)
class CapacitacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'area_responsable', 'fecha_inicio', 'cupo_maximo', 'get_inscriptos', 'cupos_disponibles', 'estado_inscripcion')
    list_filter = ('area_responsable', 'estado_inscripcion')
    search_fields = ('nombre',)
    exclude = ('area_responsable',)

    def get_fieldsets(self, request, obj=None):
        fields = ['nombre', 'descripcion', ('fecha_inicio', 'cupo_maximo')]
        
        # Agregar campos de dictado
        fields.append(('dias_dictado', 'horarios'))
        fields.append('lugar')
        
        # Solo mostrar estado_inscripcion al editar
        if obj:
            fields.append('estado_inscripcion')
            
        return (
            ('Información de la Capacitación', {
                'fields': fields
            }),
        )

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        funcionario = getattr(request.user, 'funcionario_link', None)
        if funcionario:
            nombre_area = funcionario.area.nombre.lower() if funcionario.area else ""
            nombre_depto = funcionario.departamento.nombre.lower() if funcionario.departamento else ""
            nombre_oficina = funcionario.oficina.nombre.lower() if funcionario.oficina else ""
            nombre_dir = funcionario.direccion.nombre.lower() if funcionario.direccion else ""
            
            if 'seguridad alimentaria' in nombre_depto:
                initial['area_responsable'] = 'ASAC'
            elif 'producc' in nombre_area:
                initial['area_responsable'] = 'PRODUCCION'
            elif 'quinquela' in nombre_oficina or 'cultura' in nombre_dir:
                initial['area_responsable'] = 'QUINQUELA'
        return initial

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

    def get_inscriptos(self, obj):
        return obj.cupos_ocupados
    get_inscriptos.short_description = 'Inscriptos'

    def cupos_disponibles(self, obj):
        return obj.cupos_disponibles
    cupos_disponibles.short_description = 'Disponibles'

@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('capacitacion', 'vecino', 'fecha_inscripcion', 'estado', 'ver_certificado')
    list_filter = ('estado', 'capacitacion__area_responsable')
    search_fields = ('vecino__user__first_name', 'vecino__user__last_name', 'vecino__user__username', 'capacitacion__nombre')
    actions = ['marcar_como_finalizado']

    def ver_certificado(self, obj):
        if obj.estado == 'FINALIZADO':
            from django.urls import reverse
            from django.utils.html import format_html
            url = reverse('capacitaciones:descargar_certificado', args=[obj.id])
            return format_html('<a class="button" href="{}" target="_blank">📄 Ver/Generar</a>', url)
        return "N/A"
    ver_certificado.short_description = "Certificado"

    @admin.action(description="Marcar como Finalizado/Asistió (Habilita Certificado)")
    def marcar_como_finalizado(self, request, queryset):
        rows_updated = queryset.update(estado='FINALIZADO')
        if rows_updated == 1:
            message_bit = "1 inscripción fue marcada"
        else:
            message_bit = f"{rows_updated} inscripciones fueron marcadas"
        self.message_user(request, f"{message_bit} como Finalizado.")

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
