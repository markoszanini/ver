from django.contrib import admin
from django.shortcuts import render
from django.contrib import messages
from django.db import models
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
    list_display = ('apellido', 'nombre', 'cuit_cuil', 'localidad', 'estado')
    search_fields = ('apellido', 'nombre', 'cuit_cuil', 'dni')
    list_filter = ('estado', 'localidad')
    exclude = ('estado',)

    fieldsets = (
        ('Información Personal', {
            'fields': (
                ('dni', 'cuit_cuil'),
                ('apellido', 'nombre'),
                ('telefono', 'email'),
                ('calle', 'altura'),
                'localidad',
                'observaciones',
            )
        }),
    )

    inlines = [ApicultorInstitucionalInline, ApicultorProductivoInline, ApicultorCapacitacionInline]

    class Media:
        js = ('js/apicultor_admin.js?v=15',)
        css = {
            'all': ('css/apicultura_admin.css?v=15',)
        }

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
            'apicultor': f"{e.apicultor.apellido}, {e.apicultor.nombre}",
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
            dic['pago_10'] = float(liq_total.importe_retencion if liq_total and liq_total.importe_retencion else 0)
            dic['servicio_ext'] = float(liq_ext.importe_retencion if liq_ext and liq_ext.importe_retencion else 0)
            dic['servicio_mant'] = float(liq_mant.importe_retencion if liq_mant and liq_mant.importe_retencion else 0)
            dic['municipalidad'] = float(liq_muni.importe_retencion if liq_muni and liq_muni.importe_retencion else 0)

            totales['sum_bruto'] += dic['total_bruto']
            totales['sum_10'] += dic['pago_10']
            totales['sum_serv_ext'] += dic['servicio_ext']
            totales['sum_serv_mant'] += dic['servicio_mant']
            totales['sum_muni'] += dic['municipalidad']
        else:
            dic['pago_10'] = float(liq_total.kg_retencion if liq_total and liq_total.kg_retencion else 0)
            dic['servicio_ext'] = float(liq_ext.kg_retencion if liq_ext and liq_ext.kg_retencion else 0)
            dic['servicio_mant'] = float(liq_mant.kg_retencion if liq_mant and liq_mant.kg_retencion else 0)
            dic['municipalidad'] = float(liq_muni.kg_retencion if liq_muni and liq_muni.kg_retencion else 0)

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
    readonly_fields = ('porcentaje_total', 'kg_retencion', 'importe_retencion', 'forma_pago', 'tipo_concepto', 'sub_porcentaje')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Extraccion)
class ExtraccionAdmin(admin.ModelAdmin):
    list_display = ('id_extraccion', 'apicultor', 'fecha_extraccion', 'total_kg', 'forma_pago')
    search_fields = ('apicultor__apellido', 'apicultor__nombre')
    list_filter = ('forma_pago', 'temporada', 'fecha_extraccion')
    inlines = [LiquidacionExtraccionInline]
    actions = [imprimir_acta_balance]

    fieldsets = (
        (None, {
            'fields': ('apicultor', 'fecha_extraccion', 'forma_pago', 'total_kg', 'precio_por_kg', 'observaciones')
        }),
        ('Información de Auditoría', {
            'classes': ('collapse',),
            'fields': ('nro_consecutivo', 'fecha_carga', 'id_operador'),
        }),
    )
    readonly_fields = ('fecha_carga', 'id_operador', 'nro_consecutivo')

    from django.forms import Textarea
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
    }

    class Media:
        js = ('js/apicultor_admin.js?v=11',)
        css = {
            'all': ('css/apicultura_admin.css?v=11',)
        }

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.id_operador = request.user.username
            # Generar nro_consecutivo (ej: EXT-2024-001)
            from django.utils import timezone
            year = timezone.now().year
            last_ext = Extraccion.objects.filter(nro_consecutivo__contains=f"EXT-{year}").order_by('-id_extraccion').first()
            if last_ext and last_ext.nro_consecutivo:
                try:
                    last_num = int(last_ext.nro_consecutivo.split('-')[-1])
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1
            obj.nro_consecutivo = f"EXT-{year}-{new_num:03d}"
            
        super().save_model(request, obj, form, change)
