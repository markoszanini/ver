from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import Reclamo, PaseReclamo, MensajeReclamo

class PaseReclamoInline(admin.TabularInline):
    model = PaseReclamo
    extra = 0
    fields = ('area_destino', 'oficina_destino', 'observacion', 'fecha_pase', 'usuario_emisor')
    readonly_fields = ('fecha_pase', 'usuario_emisor')
    
    def has_change_permission(self, request, obj=None):
        return False

class MensajeReclamoInline(admin.TabularInline):
    model = MensajeReclamo
    extra = 0
    fields = ('mensaje', 'fecha', 'autor', 'es_empleado')
    readonly_fields = ('fecha', 'autor', 'es_empleado')

@admin.register(Reclamo)
class ReclamoAdmin(admin.ModelAdmin):
    list_display = ('id', 'vecino', 'area', 'tipo_reclamo', 'estado', 'fecha_creacion')
    list_filter = ('area', 'estado', 'fecha_creacion')
    search_fields = ('vecino__user__first_name', 'vecino__user__last_name', 'vecino__dni', 'tipo_reclamo', 'calle', 'barrio')
    readonly_fields = ('vecino', 'area', 'tipo_reclamo', 'calle', 'numero', 'barrio', 'observacion', 'foto', 'fecha_creacion', 'fecha_actualizacion')
    list_editable = ('estado',)

    inlines = [PaseReclamoInline, MensajeReclamoInline]

    fieldsets = (
        ('Datos del Vecino', {
            'fields': ('vecino',)
        }),
        ('Información del Reclamo', {
            'fields': ('area', 'tipo_reclamo', 'estado', 'foto')
        }),
        ('Ubicación (Solo Lectura)', {
            'fields': ('calle', 'numero', 'barrio')
        }),
        ('Detalles (Solo Lectura)', {
            'fields': ('observacion',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion')
        })
    )

    def has_add_permission(self, request):
        return False

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if object_id:
            MensajeReclamo.objects.filter(reclamo_id=object_id, es_empleado=False, leido=False).update(leido=True)
        return super().change_view(request, object_id, form_url, extra_context)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, MensajeReclamo):
                if not instance.pk:  # Mensaje nuevo
                    instance.es_empleado = True
                    instance.autor = request.user
                    # Enviar email al vecino
                    email_vecino = instance.reclamo.vecino.user.email
                    if email_vecino:
                        send_mail(
                            subject=f'Nueva respuesta en reclamo #{instance.reclamo.id}',
                            message=f'Hola {instance.reclamo.vecino.user.first_name},\n\nTienes una nueva consulta o respuesta de tu reclamo: "{instance.mensaje}"\n\nPor favor, ingresa al portal de autogestión para responder.',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[email_vecino],
                            fail_silently=True,
                        )
            elif isinstance(instance, PaseReclamo):
                if not instance.pk:
                    instance.usuario_emisor = request.user
            instance.save()
        formset.save_m2m()
