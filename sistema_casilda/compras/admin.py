from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import OrdenCompra, DetalleOrdenCompra, SeguimientoOC

class DetalleOrdenCompraInline(admin.TabularInline):
    model = DetalleOrdenCompra
    
    def get_extra(self, request, obj=None, **kwargs):
        return 10 if not obj else 0

    def get_fields(self, request, obj=None):
        return ('cantidad_pedida', 'descripcion')

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.estado == 'Finalizado':
            return ('cantidad_pedida', 'descripcion')
        return self.readonly_fields or ()

@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('nro_oc', 'seccion_solicita', 'fecha_solicitud', 'estado')
    search_fields = ('nro_oc', 'seccion_solicita', 'destino')
    list_filter = ('estado', 'fecha_solicitud')
    inlines = [DetalleOrdenCompraInline]

    def changelist_view(self, request, extra_context=None):
        # Redirigir directamente al formulario de creación para saltearse el listado
        return redirect(reverse('admin:compras_ordencompra_add'))

    def get_fieldsets(self, request, obj=None):
        return (
            ('Datos de Orden', {
                'fields': (
                    ('nro_oc', 'fecha_solicitud'),
                    ('seccion_solicita', 'registrado_por'),
                    ('destino', 'origen_fondos'),
                    ('observaciones', 'archivo_orden'),
                )
            }),
        )

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.estado == 'Finalizado':
            return [f.name for f in self.model._meta.fields]
        return self.readonly_fields if self.readonly_fields else ()

    def save_formset(self, request, form, formset, change):
        # Solo validamos los detalles de la orden (no otros formsets si hubiera)
        if formset.model == DetalleOrdenCompra and not change:
            instances = formset.save(commit=False)
            if not instances:
                # No se llenó ningún ítem, lanzar error
                from django.core.exceptions import ValidationError
                raise ValidationError("Debe ingresar al menos un producto con cantidad y detalle para guardar la orden.")
        formset.save()

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        from django.core.exceptions import ValidationError
        try:
            return super().changeform_view(request, object_id, form_url, extra_context)
        except ValidationError as e:
            self.message_user(request, e.message, level=messages.ERROR)
            return redirect(reverse('admin:compras_ordencompra_add'))

# --- VISTA DE SEGUIMIENTO (Recepción / Finalización) ---

class SeguimientoDetalleInline(admin.TabularInline):
    model = DetalleOrdenCompra
    can_delete = False
    extra = 0
    fields = ('cantidad_pedida', 'descripcion', 'estado', 'observaciones')
    readonly_fields = ('cantidad_pedida', 'descripcion')

    def has_add_permission(self, request, obj):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.estado == 'Finalizado':
            return ('cantidad_pedida', 'descripcion', 'estado', 'observaciones')
        return self.readonly_fields

@admin.register(SeguimientoOC)
class SeguimientoOCAdmin(admin.ModelAdmin):
    list_display = ('nro_oc', 'seccion_solicita', 'fecha_solicitud', 'estado')
    search_fields = ('nro_oc', 'seccion_solicita', 'destino')
    list_filter = ('estado', 'fecha_solicitud')
    inlines = [SeguimientoDetalleInline]
    
    # Todos los datos originales son de solo lectura aquí por defecto
    readonly_fields = (
        'nro_oc', 'fecha_solicitud', 'seccion_solicita', 'registrado_por',
        'destino', 'origen_fondos', 'observaciones', 'archivo_orden'
    )

    def get_fieldsets(self, request, obj=None):
        return (
            ('Datos Originales de la Orden (Solo Lectura)', {
                'fields': (
                    ('nro_oc', 'fecha_solicitud'),
                    ('seccion_solicita', 'registrado_por'),
                    ('destino', 'origen_fondos'),
                    ('observaciones', 'archivo_orden'),
                )
            }),
            ('Recepción / Cierre de Orden', {
                'fields': (
                    'estado',
                    ('fecha_entrega', 'quien_entrego'),
                    'observacion_entrega'
                )
            })
        )

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.estado == 'Finalizado':
            # Todo es de solo lectura si está finalizado
            return [f.name for f in self.model._meta.fields]
        return self.readonly_fields

    def has_add_permission(self, request):
        # El seguimiento es solo para ordenes ya creadas.
        return False

@admin.register(DetalleOrdenCompra)
class DetalleOrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('orden_compra', 'item', 'descripcion', 'cantidad_pedida')
    search_fields = ('descripcion', 'orden_compra__nro_oc')
    
    def has_module_permission(self, request):
        # Hide DetalleOrdenCompra strictly from the side menu to avoid confusion
        return False
