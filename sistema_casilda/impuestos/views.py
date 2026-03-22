from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Impuesto, Deuda

@login_required
def mis_impuestos(request):
    if not hasattr(request.user, 'vecino_profile'):
        messages.error(request, 'Solo los vecinos registrados pueden acceder a esta sección.')
        return redirect('portal:home')
    
    vecino = request.user.vecino_profile
    impuestos = Impuesto.objects.filter(vecino=vecino)
    
    return render(request, 'impuestos/mis_impuestos.html', {
        'impuestos': impuestos
    })

@login_required
def estado_cuenta(request, impuesto_id):
    if not hasattr(request.user, 'vecino_profile'):
        return redirect('portal:home')
    
    vecino = request.user.vecino_profile
    impuesto = get_object_or_404(Impuesto, id=impuesto_id, vecino=vecino)
    deudas = impuesto.deudas.all().order_by('-fecha_vencimiento')
    
    return render(request, 'impuestos/estado_cuenta.html', {
        'impuesto': impuesto,
        'deudas': deudas
    })

@login_required
def simular_pago(request, deuda_id):
    if request.method == 'POST':
        deuda = get_object_or_404(Deuda, id=deuda_id, impuesto__vecino=request.user.vecino_profile)
        if deuda.estado != 'PAGADO':
            deuda.estado = 'PAGADO'
            deuda.fecha_pago = timezone.now()
            deuda.monto_original = deuda.monto_actualizado  # update the principal to the fine amount
            deuda.save()
            messages.success(request, f'El pago de la deuda del periodo {deuda.periodo} fue procesado con éxito (Simulación).')
        return redirect('impuestos:estado_cuenta', impuesto_id=deuda.impuesto.id)
    return redirect('impuestos:mis_impuestos')
