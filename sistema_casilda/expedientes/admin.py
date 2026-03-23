from django.contrib import admin
from .models import Expediente, MovimientoExpediente

@admin.register(Expediente)
class ExpedienteAdmin(admin.ModelAdmin):
    list_display = ('nro_expediente', 'asunto', 'fecha_ingreso', 'estado', 'actual_departamento', 'actual_oficina')
    search_fields = ('nro_expediente', 'asunto')
    list_filter = ('estado', 'fecha_ingreso')
    
    class Media:
        js = ('js/expedientes_admin.js',)

    def get_exclude(self, request, obj=None):
        excludes = ['registrado_por', 'origen_area', 'origen_direccion', 'origen_departamento', 'origen_oficina', 
                   'actual_area', 'actual_direccion', 'actual_departamento', 'actual_oficina', 'fecha_salida']
        
        funcionario = getattr(request.user, 'funcionario_link', None)
        is_mesa_entrada = funcionario and funcionario.departamento and 'mesa de entrada' in funcionario.departamento.nombre.lower()
        
        if not is_mesa_entrada:
            excludes.extend(['nro_expediente', 'estado', 'vecino_titular'])
        return excludes

    def save_model(self, request, obj, form, change):
        funcionario = getattr(request.user, 'funcionario_link', None)
        is_mesa_entrada = funcionario and funcionario.departamento and 'mesa de entrada' in funcionario.departamento.nombre.lower()
        
        if not obj.pk: # Nuevo Expediente creado
            if funcionario:
                obj.origen_area = funcionario.area
                obj.origen_departamento = funcionario.departamento
                obj.origen_direccion = funcionario.direccion
                obj.origen_oficina = funcionario.oficina
                
            if not is_mesa_entrada:
                # Va directo a mesa de entrada
                from organigrama.models import Departamento
                mesa = Departamento.objects.filter(nombre__icontains='mesa de entrada').first()
                if mesa:
                    obj.actual_departamento = mesa
                    obj.actual_area = mesa.direccion.area if mesa.direccion else None
                obj.estado = 'Pendiente de Asignación'
                
            else:
                # Si lo crea mesa de entrada directamente, lo atajan ellos
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
            
        from django.db.models import Q
        q_origen = Q()
        q_actual = Q()
        
        if area:
            q_origen |= Q(origen_area=area)
            q_actual |= Q(actual_area=area)
        if depto:
            q_origen |= Q(origen_departamento=depto)
            q_actual |= Q(actual_departamento=depto)
        if oficina:
            q_origen |= Q(origen_oficina=oficina)
            q_actual |= Q(actual_oficina=oficina)
            
        return qs.filter(q_origen | q_actual).distinct()

    def has_add_permission(self, request):
        # Todos pueden crear notas internas (expedientes sin nro) que van a mesa de entrada
        return True

@admin.register(MovimientoExpediente)
class MovimientoExpedienteAdmin(admin.ModelAdmin):
    list_display = ('expediente', 'fecha_pase', 'destino_departamento', 'destino_oficina', 'estado', 'usuario_emisor')
    search_fields = ('expediente__nro_expediente',)
    list_filter = ('estado', 'fecha_pase')

    class Media:
        js = ('js/expedientes_admin.js',)

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
                    
                    # Mesa de entrada puede hacer pases de cualquier cosa que tenga ahí, u originado por ellos.
                    if funcionario.departamento and 'mesa de entrada' in funcionario.departamento.nombre.lower():
                        kwargs["queryset"] = Expediente.objects.all()
                    else:
                        kwargs["queryset"] = Expediente.objects.filter(q_actual).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.pk: # Creando un nuevo pase
            obj.usuario_emisor = request.user.username
            # Automáticamente derivar el Expediente a su nueva ubicación actual
            exp = obj.expediente
            exp.actual_area = obj.destino_area
            exp.actual_departamento = obj.destino_departamento
            exp.actual_direccion = obj.destino_direccion
            exp.actual_oficina = obj.destino_oficina
            if obj.estado:
                exp.estado = obj.estado
            exp.save()
        super().save_model(request, obj, form, change)
