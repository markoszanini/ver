from .models import MensajeReclamo, PaseReclamo

def unread_messages_processor(request):
    unread_vecino_count = 0
    if hasattr(request, 'user') and request.user.is_authenticated:
        if hasattr(request.user, 'vecino_profile'):
            mensajes_count = MensajeReclamo.objects.filter(
                reclamo__vecino=request.user.vecino_profile,
                es_empleado=True,
                leido=False
            ).count()
            pases_count = PaseReclamo.objects.filter(
                reclamo__vecino=request.user.vecino_profile,
                leido_por_vecino=False
            ).count()
            unread_vecino_count = mensajes_count + pases_count
    return {'unread_vecino_count': unread_vecino_count}
