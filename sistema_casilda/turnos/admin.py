from django.contrib import admin
from django.contrib import messages
from .models import ConfiguracionTurno, Turno

@admin.register(ConfiguracionTurno)
class ConfiguracionTurnoAdmin(admin.ModelAdmin):
    list_display = ('tipo_turno', 'hora_inicio', 'hora_fin', 'turnos_por_hora', 'dias_habiles')

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'hora', 'tipo_turno', 'vecino', 'estado')
    list_filter = ('fecha', 'tipo_turno', 'estado')
    search_fields = ('vecino__user__first_name', 'vecino__user__last_name', 'vecino__user__username')
    date_hierarchy = 'fecha'
    actions = ['aprobar_turnos', 'rechazar_turnos']
    
    # Hacer todos los campos de solo lectura para evitar alteraciones de turnos agendados,
    # el empleado sólo debería usar las acciones masivas para aprobar o rechazar.
    readonly_fields = ('vecino', 'tipo_turno', 'fecha', 'hora', 'fecha_solicitud', 'tipo_licencia', 'vencimiento_licencia', 'observaciones')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
            
        funcionario = getattr(request.user, 'funcionario_link', None)
        if funcionario:
            nombre_area = funcionario.area.nombre.lower() if funcionario.area else ""
            nombre_depto = funcionario.departamento.nombre.lower() if funcionario.departamento else ""
            
            allowed_types = []
            if 'gobierno' in nombre_area and 'tránsito' in nombre_depto:
                allowed_types.append('LICENCIA')
            if 'desarrollo' in nombre_area and 'bienestar' in nombre_area:
                allowed_types.append('PSICOFISICO')
                
            return qs.filter(tipo_turno__in=allowed_types)
        return qs.none() # Fallback, si no matchea nada ve vacío.

    # Limitar de forma dinámica los filtros a sólo lo que puede ver el usuario
    def get_list_filter(self, request):
        filtros = super().get_list_filter(request)
        if not request.user.is_superuser:
            funcionario = getattr(request.user, 'funcionario_link', None)
            if funcionario:
                nombre_area = funcionario.area.nombre.lower() if funcionario.area else ""
                nombre_depto = funcionario.departamento.nombre.lower() if funcionario.departamento else ""
                # Si sólo tiene acceso a un tipo, quitamos el filtro por tipo de turno porque no tiene sentido
                if not ('gobierno' in nombre_area and 'tránsito' in nombre_depto) or not ('desarrollo' in nombre_area and 'bienestar' in nombre_area):
                    return ('fecha', 'estado')
        return filtros

    @admin.action(description="Aprobar turnos seleccionados")
    def aprobar_turnos(self, request, queryset):
        queryset.update(estado='APROBADO')
        self.message_user(request, "Turnos aprobados correctamente.", messages.SUCCESS)

    @admin.action(description="Rechazar turnos seleccionados")
    def rechazar_turnos(self, request, queryset):
        queryset.update(estado='RECHAZADO')
        self.message_user(request, "Turnos rechazados correctamente.", messages.WARNING)
