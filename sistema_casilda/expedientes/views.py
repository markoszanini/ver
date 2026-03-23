from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Expediente

@login_required
def mis_expedientes(request):
    vecino = getattr(request.user, 'vecino_profile', None)
    if not vecino:
        return render(request, 'portal/error_vecino.html', {'mensaje': 'Sólo vecinos registrados pueden ver expedientes.'})
    
    expedientes = Expediente.objects.filter(vecino_titular=vecino).order_by('-fecha_ingreso')
    return render(request, 'expedientes/mis_expedientes.html', {'expedientes': expedientes})

@login_required
def seguimiento_expediente(request, id_expediente):
    vecino = getattr(request.user, 'vecino_profile', None)
    if not vecino:
        return render(request, 'portal/error_vecino.html', {'mensaje': 'Acceso denegado.'})
        
    expediente = get_object_or_404(Expediente, id_expediente=id_expediente, vecino_titular=vecino)
    movimientos = expediente.movimientos.all().order_by('fecha_pase') # Ascending order to show timeline
    
    return render(request, 'expedientes/seguimiento.html', {
        'expediente': expediente,
        'movimientos': movimientos
    })
