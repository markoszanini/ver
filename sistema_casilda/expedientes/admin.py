from django.contrib import admin
from .models import Expediente, MovimientoExpediente

@admin.register(Expediente)
class ExpedienteAdmin(admin.ModelAdmin):
    list_display = ('nro_expediente', 'get_origen', 'asunto', 'dirigido_a', 'fecha_ingreso', 'estado', 'confirmado', 'get_ubicacion')
    search_fields = ('nro_expediente', 'asunto', 'dni_titular_manual', 'nombre_titular_manual', 'apellido_titular_manual')
    list_filter = ('confirmado', 'estado', 'fecha_ingreso')
    readonly_fields = ('nro_expediente', 'registrado_por', 'get_origen', 'get_ubicacion', 'confirmado')
    actions = ['confirmar_expedientes']
    
    class Media:
        js = ('js/expedientes_admin.js',)

    def get_fieldsets(self, request, obj=None):
        return (
            (None, {
                'fields': ('nro_expediente', 'get_origen', 'asunto', 'get_ubicacion', 'estado')
            }),
            ('Titular del Trámite (Vecinos)', {
                'fields': ('vecino_titular',),
                'description': 'Seleccione si el vecino ya está registrado en el portal.'
            }),
            ('Titular No Registrado (Carga Manual)', {
                'fields': ('dni_titular_manual', 'nombre_titular_manual', 'apellido_titular_manual'),
                'description': 'Use estos campos solo si el vecino aún no tiene cuenta.',
                'classes': ('collapse',)
            }),
            ('Solicitud Interna (Staff)', {
                'fields': ('dirigido_a', 'oficina_destino_sugerida'),
                'description': 'Información para expedientes generados internamente.'
            }),
            ('Detalles adicionales', {
                'fields': ('foto', 'observaciones'),
            }),
        )

    @admin.display(description='Origen')
    def get_origen(self, obj):
        return obj.origen_display

    @admin.display(description='Ubicación Actual')
    def get_ubicacion(self, obj):
        return obj.ubicacion_display

    @admin.action(description='Confirmar y Asignar Número (Mesa Entrada)')
    def confirmar_expedientes(self, request, queryset):
        # Solo Mesa Entrada puede confirmar
        funcionario = getattr(request.user, 'funcionario_link', None)
        is_mesa = False
        if funcionario and funcionario.departamento and 'mesa de entrada' in funcionario.departamento.nombre.lower():
            is_mesa = True
            
        if not is_mesa and not request.user.is_superuser:
            self.message_user(request, "Solo personal de Mesa de Entradas puede confirmar expedientes.", level='error')
            return

        cant = 0
        for obj in queryset.filter(confirmado=False):
            obj.confirmado = True
            obj.registrado_por = request.user.username
            # Al guardar con confirmado=True, el modelo asigna el nro_expediente
            obj.save()
            cant += 1
        
        self.message_user(request, f"Se confirmaron {cant} expedientes con éxito.")

    def save_model(self, request, obj, form, change):
        funcionario = getattr(request.user, 'funcionario_link', None)
        
        is_mesa_entrada = False
        if funcionario and funcionario.departamento:
            if 'mesa de entrada' in funcionario.departamento.nombre.lower():
                is_mesa_entrada = True
        
        if not obj.pk: # Nuevo Expediente creado
            obj.creado_por = request.user
            if funcionario:
                obj.solicitante_interno = funcionario
                obj.origen_area = funcionario.area
                obj.origen_departamento = funcionario.departamento
                obj.origen_direccion = funcionario.direccion
                obj.origen_oficina = funcionario.oficina
                
            if not is_mesa_entrada:
                # Va directo a mesa de entrada pero NO se confirma aún
                obj.confirmado = False
                from organigrama.models import Departamento
                mesa = Departamento.objects.filter(nombre__icontains='mesa de entrada').first()
                if mesa:
                    obj.actual_departamento = mesa
                    obj.actual_area = mesa.direccion.area if mesa.direccion else None
                obj.estado = 'Pendiente de Confirmación'
            else:
                # Si lo crea mesa de entrada directamente, ya sale confirmado
                obj.confirmado = True
                if funcionario:
                    obj.actual_departamento = funcionario.departamento
                    obj.actual_area = funcionario.area
                obj.estado = 'En trámite'
                obj.registrado_por = request.user.username
                
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        funcionario = getattr(request.user, 'funcionario_link', None)
        if not funcionario:
            return qs.none()
            
        depto = funcionario.departamento
        area = funcionario.area
        oficina = funcionario.oficina
        
        # Si es departamento Mesa de Entrada, ve todos
        if depto and 'mesa de entrada' in depto.nombre.lower():
            return qs
            
        # Staff ve los de su área O los que creó él (aunque no estén confirmados)
        from django.db.models import Q
        q_origen = Q()
        q_actual = Q()
        q_creador = Q(creado_por=request.user)
        
        if area:
            q_origen |= Q(origen_area=area)
            q_actual |= Q(actual_area=area)
        if depto:
            q_origen |= Q(origen_departamento=depto)
            q_actual |= Q(actual_area=area) # Si depto está en área Mesa Entrada, ve todos
            q_actual |= Q(actual_departamento=depto)
        if oficina:
            q_origen |= Q(origen_oficina=oficina)
            q_actual |= Q(actual_oficina=oficina)
            
        return qs.filter(q_origen | q_actual | q_creador).distinct()

    def has_add_permission(self, request):
        return True

@admin.register(MovimientoExpediente)
class MovimientoExpedienteAdmin(admin.ModelAdmin):
    list_display = ('expediente', 'fecha_pase', 'get_destino', 'estado', 'usuario_emisor')
    search_fields = ('expediente__nro_expediente',)
    list_filter = ('estado', 'fecha_pase')

    class Media:
        js = ('js/expedientes_admin.js',)

    @admin.display(description='Destino')
    def get_destino(self, obj):
        if obj.destino_oficina: return f"Ofi: {obj.destino_oficina.nombre}"
        if obj.destino_departamento: return f"Depto: {obj.destino_departamento.nombre}"
        return str(obj.destino_area) if obj.destino_area else "-"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "expediente":
            if not request.user.is_superuser:
                funcionario = getattr(request.user, 'funcionario_link', None)
                if funcionario:
                    from django.db.models import Q
                    q_actual = Q()
                    if funcionario.area: q_actual |= Q(actual_area=funcionario.area)
                    if funcionario.departamento: q_actual |= Q(actual_departamento=funcionario.departamento)
                    if funcionario.oficina: q_actual |= Q(actual_oficina=funcionario.oficina)
                    
                    if funcionario.departamento and 'mesa de entrada' in funcionario.departamento.nombre.lower():
                        kwargs["queryset"] = Expediente.objects.all()
                    else:
                        kwargs["queryset"] = Expediente.objects.filter(q_actual).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario_emisor = request.user.username
            exp = obj.expediente
            exp.actual_area = obj.destino_area
            exp.actual_direccion = obj.destino_direccion
            exp.actual_departamento = obj.destino_departamento
            exp.actual_oficina = obj.destino_oficina
            
            # Cascada inteligente
            if exp.actual_oficina:
                if not exp.actual_area: exp.actual_area = exp.actual_oficina.area
                if not exp.actual_direccion: exp.actual_direccion = exp.actual_oficina.direccion
                if not exp.actual_departamento and exp.actual_oficina.division:
                    exp.actual_departamento = exp.actual_oficina.division.departamento
            
            if exp.actual_departamento:
                if not exp.actual_area: exp.actual_area = exp.actual_departamento.area
                if not exp.actual_direccion: exp.actual_direccion = exp.actual_departamento.direccion

            if obj.estado:
                exp.estado = obj.estado
            exp.save()
        super().save_model(request, obj, form, change)
