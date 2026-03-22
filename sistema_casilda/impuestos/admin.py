from django.contrib import admin
from django.contrib import messages
from django.utils.timezone import now
from .models import PartidaInmobiliaria, Impuesto, Deuda

class DeudaInline(admin.TabularInline):
    model = Deuda
    extra = 1

@admin.register(PartidaInmobiliaria)
class PartidaInmobiliariaAdmin(admin.ModelAdmin):
    list_display = ('nomenclatura', 'direccion', 'vecino')
    search_fields = ('nomenclatura', 'direccion')
    raw_id_fields = ('vecino',)

@admin.register(Impuesto)
class ImpuestoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'tipo', 'vecino', 'partida')
    list_filter = ('tipo',)
    search_fields = ('vecino__user__first_name', 'vecino__user__last_name', 'vecino__user__username', 'partida__nomenclatura')
    raw_id_fields = ('vecino', 'partida')
    inlines = [DeudaInline]

@admin.register(Deuda)
class DeudaAdmin(admin.ModelAdmin):
    list_display = ('impuesto', 'periodo', 'monto_original', 'fecha_vencimiento', 'monto_actualizado', 'estado')
    list_filter = ('estado', 'fecha_vencimiento')
    search_fields = ('impuesto__vecino__user__username', 'impuesto__partida__nomenclatura', 'periodo')
    actions = ['marcar_pagado', 'enviar_recordatorio']

    @admin.action(description="Marcar deudas seleccionadas como PAGADO")
    def marcar_pagado(self, request, queryset):
        queryset.update(estado='PAGADO', fecha_pago=now())
        self.message_user(request, "Las deudas fueron marcadas como pagadas.", messages.SUCCESS)

    @admin.action(description="Enviar recordatorio de vencimiento (Simulado)")
    def enviar_recordatorio(self, request, queryset):
        count = queryset.count()
        self.message_user(request, f"Se prepararon {count} correos de recordatorio de vencimiento que serán enviados a los vecinos.", messages.SUCCESS)
