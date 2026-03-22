from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Reclamo, MensajeReclamo, PaseReclamo
from .forms import ReclamoForm
from portal.models import Vecino

@login_required
def mis_reclamos(request):
    if not hasattr(request.user, 'vecino_profile'):
        messages.error(request, "Perfil de vecino no encontrado.")
        return redirect('portal:dashboard')

    vecino = request.user.vecino_profile

    reclamos = Reclamo.objects.filter(vecino=vecino).order_by('-fecha_creacion')
    return render(request, 'reclamos/mis_reclamos.html', {'reclamos': reclamos})

@login_required
def nuevo_reclamo(request):
    if not hasattr(request.user, 'vecino_profile'):
        messages.error(request, "Perfil de vecino no encontrado.")
        return redirect('portal:dashboard')

    vecino = request.user.vecino_profile

    if request.method == 'POST':
        form = ReclamoForm(request.POST, request.FILES)
        if form.is_valid():
            reclamo = form.save(commit=False)
            reclamo.vecino = vecino
            reclamo.save()
            messages.success(request, 'Su reclamo ha sido registrado exitosamente.')
            return redirect('reclamos:mis_reclamos')
        else:
            messages.error(request, 'Hubo un error al procesar el formulario. Verifique los datos.')
    else:
        form = ReclamoForm()

    return render(request, 'reclamos/nuevo_reclamo.html', {'form': form})

@login_required
def detalle_reclamo(request, reclamo_id):
    if not hasattr(request.user, 'vecino_profile'):
        messages.error(request, "Perfil de vecino no encontrado.")
        return redirect('portal:dashboard')

    vecino = request.user.vecino_profile
    reclamo = get_object_or_404(Reclamo, id=reclamo_id, vecino=vecino)
    
    # Marcar mensajes del empleado como leídos por el vecino
    MensajeReclamo.objects.filter(reclamo=reclamo, es_empleado=True, leido=False).update(leido=True)
    
    # Marcar pases como leídos por el vecino
    PaseReclamo.objects.filter(reclamo=reclamo, leido_por_vecino=False).update(leido_por_vecino=True)
    
    mensajes = MensajeReclamo.objects.filter(reclamo=reclamo).order_by('fecha')
    pases = reclamo.pases.all().order_by('fecha_pase')
    puede_responder = mensajes.filter(es_empleado=True).exists()

    if request.method == 'POST' and puede_responder:
        texto_mensaje = request.POST.get('mensaje', '').strip()
        if texto_mensaje:
            MensajeReclamo.objects.create(
                reclamo=reclamo,
                mensaje=texto_mensaje,
                es_empleado=False,
                autor=request.user
            )
            messages.success(request, 'Su respuesta ha sido enviada al municipio.')
            return redirect('reclamos:detalle_reclamo', reclamo_id=reclamo.id)

    return render(request, 'reclamos/detalle_reclamo.html', {
        'reclamo': reclamo,
        'mensajes': mensajes,
        'pases': pases,
        'puede_responder': puede_responder
    })

@login_required
def admin_unread_count(request):
    if not request.user.is_staff:
        return JsonResponse({'unread_count': 0})
    count = MensajeReclamo.objects.filter(es_empleado=False, leido=False).count()
    return JsonResponse({'unread_count': count})
