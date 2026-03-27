from django.contrib import admin
from .models import (
    ReciboSueldo, Vacaciones, NovedadRRHH, 
    CategoriaSalarial, InformacionSalarial, LiquidacionMensual,
    Familiar, FormacionAcademica, ExperienciaLaboral, Empleado
)
from organigrama.forms import FuncionarioForm
from django.utils import timezone
from .utils import GeneradorReciboPDF
from django.contrib import messages
from django.db import transaction

@admin.action(description="Generar Liquidación Mes Actual")
def liquidar_mes(modeladmin, request, queryset):
    generador = GeneradorReciboPDF()
    hoy = timezone.now()
    mes_actual = hoy.month
    anio_actual = hoy.year
    exitos = 0
    errores = 0

    for empleado in queryset:
        try:
            with transaction.atomic():
                # 1. Obtener Info Salarial
                try:
                    info = empleado.info_salarial
                except InformacionSalarial.DoesNotExist:
                    errores += 1
                    continue

                basico = float(info.sueldo_basico_aplicable)
                if basico <= 0:
                    errores += 1
                    continue

                # 2. Cálculos
                # Antigüedad (2% por año)
                # Usamos fecha_alta si existe, sino hoy
                fecha_alta = empleado.fecha_alta if empleado.fecha_alta else hoy
                anios_antiguedad = hoy.year - fecha_alta.year
                monto_antiguedad = basico * (anios_antiguedad * 0.02)
                
                # Título
                porc_titulo = float(info.adicional_titulo_tipo) / 100
                monto_titulo = basico * porc_titulo
                
                # Suplemento
                porc_suplemento = float(info.suplemento_tipo) / 100
                monto_suplemento = basico * porc_suplemento
                
                # Otros fijos
                otros = float(info.otros_adicionales_fijos)

                bruto = basico + monto_antiguedad + monto_titulo + monto_suplemento + otros
                
                # Descuentos (11% + 3% + 3% = 17%)
                desc_jub = bruto * 0.11
                desc_os = bruto * 0.03
                desc_ley = bruto * 0.03
                total_desc = desc_jub + desc_os + desc_ley
                
                neto = bruto - total_desc

                detalles = {
                    'remunerativos': [
                        {'nombre': 'Sueldo Básico', 'monto': basico},
                        {'nombre': f'Antigüedad ({anios_antiguedad} años)', 'monto': monto_antiguedad},
                    ],
                    'deducciones': [
                        {'nombre': 'Jubilación (11%)', 'monto': desc_jub},
                        {'nombre': 'IAPOS / Obra Social (3%)', 'monto': desc_os},
                        {'nombre': 'Ley 19032 (3%)', 'monto': desc_ley},
                    ]
                }
                
                if monto_titulo > 0:
                    detalles['remunerativos'].append({'nombre': f'Adic. Título ({info.get_adicional_titulo_tipo_display()})', 'monto': monto_titulo})
                if monto_suplemento > 0:
                    detalles['remunerativos'].append({'nombre': f'Suplemento ({info.get_suplemento_tipo_display()})', 'monto': monto_suplemento})
                if otros > 0:
                    detalles['remunerativos'].append({'nombre': 'Otros Adicionales', 'monto': otros})

                # 3. Guardar Liquidación
                liq, _ = LiquidacionMensual.objects.update_or_create(
                    funcionario=empleado,
                    mes=mes_actual,
                    anio=anio_actual,
                    defaults={
                        'sueldo_bruto': bruto,
                        'total_descuentos': total_desc,
                        'sueldo_neto': neto,
                        'detalles_json': detalles
                    }
                )

                # 4. Generar y Guardar PDF Recibo
                pdf_file = generador.generar_pdf_recibo(empleado, liq, detalles)
                
                recibo, _ = ReciboSueldo.objects.update_or_create(
                    funcionario=empleado,
                    mes=mes_actual,
                    anio=anio_actual,
                    defaults={'archivo': pdf_file}
                )
                
                exitos += 1
        except Exception as e:
            errores += 1

    modeladmin.message_user(request, f"Proceso finalizado: {exitos} liquidaciones generadas, {errores} errores.", messages.SUCCESS if exitos > 0 else messages.ERROR)

class FamiliarInline(admin.TabularInline):
    model = Familiar
    extra = 1

class FormacionAcademicaInline(admin.TabularInline):
    model = FormacionAcademica
    extra = 1

class ExperienciaLaboralInline(admin.TabularInline):
    model = ExperienciaLaboral
    extra = 1

class InformacionSalarialInline(admin.StackedInline):
    model = InformacionSalarial
    can_delete = False
    verbose_name_plural = 'Información Salarial (Liquidación)'

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    form = FuncionarioForm
    list_display = ('usuario_login', 'nombre', 'apellido', 'dni', 'activo', 'rango', 'area')
    search_fields = ('usuario_login', 'nombre', 'apellido', 'dni', 'email')
    list_filter = ('activo', 'rango', 'area', 'departamento')
    inlines = [InformacionSalarialInline, FamiliarInline, FormacionAcademicaInline, ExperienciaLaboralInline]
    actions = [liquidar_mes]

    fieldsets = (
        ('Identificación y Cuenta', {
            'classes': ('tab-datos',),
            'fields': (
                ('usuario_login', 'nro_legajo'),
                'password_nueva', 
            )
        }),
        ('Datos Personales', {
            'classes': ('tab-datos',),
            'fields': (
                ('nombre', 'segundo_nombre'),
                'apellido',
                ('dni', 'cuil'),
                ('fecha_nacimiento', 'genero'),
                ('estado_civil', 'email'),
            )
        }),
        ('Domicilio y Contacto', {
            'classes': ('tab-datos',),
            'fields': (
                ('calle', 'altura'),
                ('telefono', 'celular'),
            )
        }),
        ('Estructura Organizativa', {
            'fields': (
                'area',
                'direccion',
                'departamento',
                'division',
                'subdivision',
                'seccion',
                'oficina'
            )
        }),
        ('Categoría y Rol', {
            'fields': (
                'rango',
            )
        }),
    )

    class Media:
        js = ('js/organigrama_admin_v3.js',)
        css = {'all': ('css/multas_admin.css',)}  # reutilizamos las cajas select2 ensanchadas

@admin.register(CategoriaSalarial)
class CategoriaSalarialAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'sueldo_basico')

@admin.register(InformacionSalarial)
class InformacionSalarialAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'categoria', 'sueldo_basico_personalizado')
    search_fields = ('funcionario__nombre', 'funcionario__apellido', 'funcionario__usuario_login')

@admin.register(LiquidacionMensual)
class LiquidacionMensualAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'mes', 'anio', 'sueldo_neto')
    list_filter = ('mes', 'anio')
    readonly_fields = ('fecha_proceso',)

@admin.register(ReciboSueldo)
class ReciboSueldoAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'mes', 'anio', 'fecha_subida')
    list_filter = ('anio', 'mes', 'funcionario')
    search_fields = ('funcionario__usuario_login', 'funcionario__nombre', 'funcionario__apellido')

@admin.register(Vacaciones)
class VacacionesAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'anio_correspondiente', 'dias_totales', 'dias_tomados', 'dias_disponibles')
    search_fields = ('funcionario__usuario_login',)

@admin.register(NovedadRRHH)
class NovedadRRHHAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha', 'es_general', 'funcionario_destino')
    list_filter = ('es_general', 'fecha')
    search_fields = ('titulo', 'mensaje')
