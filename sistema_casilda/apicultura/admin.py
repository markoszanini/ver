from django.contrib import admin
from django.shortcuts import render
from django.contrib import messages
from .models import (Apicultor, Extraccion, LiquidacionExtraccion, 
                     ApicultorInstitucional, ApicultorProductivo, ApicultorCapacitacion)

class ApicultorInstitucionalInline(admin.StackedInline):
    model = ApicultorInstitucional

class ApicultorProductivoInline(admin.StackedInline):
    model = ApicultorProductivo

class ApicultorCapacitacionInline(admin.TabularInline):
    model = ApicultorCapacitacion
    extra = 0

@admin.register(Apicultor)
class ApicultorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cuit_cuil', 'localidad', 'estado')
    search_fields = ('nombre', 'cuit_cuil', 'dni')
    list_filter = ('estado', 'localidad')
    exclude = ('estado',)
    inlines = [ApicultorInstitucionalInline, ApicultorProductivoInline, ApicultorCapacitacionInline]

@admin.action(description='Imprimir Acta de Balance (Seleccionadas)')
def imprimir_acta_balance(modeladmin, request, queryset):
    # Verify all selected forms have the same forma_pago
    tipos_pago = set(queryset.values_list('forma_pago', flat=True))
    if len(tipos_pago) > 1:
        modeladmin.message_user(request, "Las extracciones seleccionadas deben tener la misma FORMA DE PAGO para generar un acta unificada.", level=messages.ERROR)
        return
    tipo_pago = list(tipos_pago)[0] if tipos_pago else 'DINERO'

    desde = queryset.order_by('fecha_extraccion').first().fecha_extraccion
    hasta = queryset.order_by('-fecha_extraccion').first().fecha_extraccion

    datos_extracciones = []
    totales = {
        'sum_kg': 0.0, 'sum_bruto': 0.0, 'sum_10': 0.0,
        'sum_serv_ext': 0.0, 'sum_serv_mant': 0.0, 'sum_muni': 0.0
    }

    for e in queryset:
        dic = {
            'id_extraccion': e.id_extraccion,
            'apicultor': e.apicultor.nombre,
            'total_kg': float(e.total_kg or 0),
        }
        totales['sum_kg'] += dic['total_kg']

        liq_total = e.liquidaciones.filter(tipo_concepto='TOTAL').first()
        liq_ext = e.liquidaciones.filter(tipo_concepto='SERV_EXT').first()
        liq_mant = e.liquidaciones.filter(tipo_concepto='SERV_MANT').first()
        liq_muni = e.liquidaciones.filter(tipo_concepto='MUNICIPALIDAD').first()

        if tipo_pago == 'DINERO':
            dic['precio_por_kg'] = float(e.precio_por_kg or 0)
            dic['total_bruto'] = dic['total_kg'] * dic['precio_por_kg']
            dic['pago_10'] = float(liq_total.importe_9_porciento if liq_total and liq_total.importe_9_porciento else 0)
            dic['servicio_ext'] = float(liq_ext.importe_9_porciento if liq_ext and liq_ext.importe_9_porciento else 0)
            dic['servicio_mant'] = float(liq_mant.importe_9_porciento if liq_mant and liq_mant.importe_9_porciento else 0)
            dic['municipalidad'] = float(liq_muni.importe_9_porciento if liq_muni and liq_muni.importe_9_porciento else 0)

            totales['sum_bruto'] += dic['total_bruto']
            totales['sum_10'] += dic['pago_10']
            totales['sum_serv_ext'] += dic['servicio_ext']
            totales['sum_serv_mant'] += dic['servicio_mant']
            totales['sum_muni'] += dic['municipalidad']
        else:
            dic['servicio_ext'] = float(liq_ext.kg_9_porciento if liq_ext and liq_ext.kg_9_porciento else 0)
            dic['servicio_mant'] = float(liq_mant.kg_9_porciento if liq_mant and liq_mant.kg_9_porciento else 0)
            dic['municipalidad'] = float(liq_muni.kg_9_porciento if liq_muni and liq_muni.kg_9_porciento else 0)

            totales['sum_serv_ext'] += dic['servicio_ext']
            totales['sum_serv_mant'] += dic['servicio_mant']
            totales['sum_muni'] += dic['municipalidad']

        datos_extracciones.append(dic)

    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=https://sistema-local/validar-acta?tipo={tipo_pago}&desde={desde.strftime('%Y%m%d')}&hasta={hasta.strftime('%Y%m%d')}"

    context = {
        'tipo_pago': tipo_pago,
        'desde': desde,
        'hasta': hasta,
        'extracciones': datos_extracciones,
        'totales': totales,
        'qr_url': qr_url,
        'app_user': request.user.username if request.user.is_authenticated else 'Desconocido',
    }
    return render(request, "admin/acta_balance.html", context)

class LiquidacionExtraccionInline(admin.TabularInline):
    model = LiquidacionExtraccion
    extra = 0
    # Hacemos que sea solo lectura ya que se autocalcula en el save() de Extraccion
    readonly_fields = ('porcentaje_total', 'kg_9_porciento', 'importe_9_porciento', 'forma_pago', 'tipo_concepto', 'sub_porcentaje')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Extraccion)
class ExtraccionAdmin(admin.ModelAdmin):
    list_display = ('id_extraccion', 'apicultor', 'fecha_extraccion', 'total_kg', 'forma_pago')
    search_fields = ('apicultor__nombre',)
    list_filter = ('forma_pago', 'temporada', 'fecha_extraccion')
    inlines = [LiquidacionExtraccionInline]
    actions = [imprimir_acta_balance]

    readonly_fields = ('fecha_carga',)
    fields = ('fecha_carga', 'apicultor', 'fecha_extraccion', 'forma_pago', 'total_kg', 'precio_por_kg', 'observaciones')

    class Media:
        js = ('js/extraccion_toggle.js?v=1',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.id_operador = request.user.username
        super().save_model(request, obj, form, change)
