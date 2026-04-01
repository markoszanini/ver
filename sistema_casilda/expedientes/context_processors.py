from .models import NotificacionExpediente, Expediente
from organigrama.models import Funcionario

def unread_notifications(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return {
            'unread_expediente_count': 0, 
            'recent_expediente_notifs': [],
            'is_mesa_staff': False
        }

    count = 0
    recent = []
    is_mesa = False
    
    try:
        funcionario = getattr(request.user, 'funcionario_link', None)
        
        if funcionario and funcionario.departamento and funcionario.departamento.nombre:
            is_mesa = 'mesa' in funcionario.departamento.nombre.lower()

        # Notificaciones estándar (Pases directos)
        count = NotificacionExpediente.objects.filter(usuario=request.user, leido=False).count()
        recent = NotificacionExpediente.objects.filter(usuario=request.user, leido=False)[:5]

        # Para Mesa de Entrada, sumamos los expedientes que esperan número (confirmado=False)
        if is_mesa:
            pendientes_folio = Expediente.objects.filter(confirmado=False).count()
            count += pendientes_folio
    except Exception:
        # Failsafe to avoid crashing every page in the portal
        pass

    return {
        'unread_expediente_count': count,
        'recent_expediente_notifs': recent,
        'is_mesa_staff': is_mesa
    }
