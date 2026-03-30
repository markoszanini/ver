from django.shortcuts import render, redirect, get_object_or_404
import os
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Capacitacion, Inscripcion

@login_required
def explorar_capacitaciones(request):
    if not hasattr(request.user, 'vecino_profile'):
        return redirect('portal:home')
        
    vecino = request.user.vecino_profile
    # Cursos disponibles (excluyendo en los que ya está anotado)
    capacitaciones_abiertas = Capacitacion.objects.filter(estado_inscripcion='ABIERTA').exclude(inscripciones__vecino=vecino)
    
    return render(request, 'capacitaciones/explorar.html', {
        'capacitaciones': capacitaciones_abiertas
    })

@login_required
def mis_capacitaciones(request):
    if not hasattr(request.user, 'vecino_profile'):
        return redirect('portal:home')
        
    vecino = request.user.vecino_profile
    inscripciones = Inscripcion.objects.filter(vecino=vecino).select_related('capacitacion').order_by('-fecha_inscripcion')
    
    return render(request, 'capacitaciones/mis_capacitaciones.html', {
        'inscripciones': inscripciones
    })

@login_required
def inscribirse_curso(request, cap_id):
    if not hasattr(request.user, 'vecino_profile'):
        return redirect('portal:home')
        
    if request.method == 'POST':
        capacitacion = get_object_or_404(Capacitacion, pk=cap_id)
        vecino = request.user.vecino_profile
        
        if capacitacion.estado_inscripcion == 'CERRADA':
            messages.error(request, "Las inscripciones para este curso ya se encuentran cerradas.")
            return redirect('capacitaciones:explorar')
            
        if Inscripcion.objects.filter(vecino=vecino, capacitacion=capacitacion).exists():
            messages.warning(request, "Ya te encuentras inscripto en este curso.")
            return redirect('capacitaciones:mis_capacitaciones')
            
        if capacitacion.cupos_disponibles <= 0:
            messages.error(request, "Lo sentimos, el cupo para este curso ya se encuentra lleno.")
            capacitacion.verificar_y_cerrar_cupo() # Auto cierre
            return redirect('capacitaciones:explorar')
            
        # Inscribir
        Inscripcion.objects.create(capacitacion=capacitacion, vecino=vecino, estado='INSCRIPTO')
        messages.success(request, f"Te has inscripto exitosamente en: {capacitacion.nombre}!")
        
        # Verificar si fue el último lugar para auto cerrar
        capacitacion.verificar_y_cerrar_cupo()
        
        return redirect('capacitaciones:mis_capacitaciones')
        
    return redirect('capacitaciones:explorar')

from .utils import generate_certificate_pdf

@login_required
def descargar_certificado(request, insc_id):
    # Allow staff to view any certificate, or restrict neighbors to their own
    if request.user.is_staff:
        inscripcion = get_object_or_404(Inscripcion, pk=insc_id)
    else:
        if not hasattr(request.user, 'vecino_profile'):
            return redirect('portal:home')
        vecino = request.user.vecino_profile
        inscripcion = get_object_or_404(Inscripcion, pk=insc_id, vecino=vecino)
    
    if inscripcion.estado != 'FINALIZADO':
        messages.error(request, "El certificado solo está disponible para capacitaciones finalizadas.")
        return redirect('capacitaciones:mis_capacitaciones')
    
    # Generate certificate if it doesn't exist
    if not inscripcion.certificado:
        pdf_content = generate_certificate_pdf(inscripcion)
        if pdf_content:
            inscripcion.certificado.save(pdf_content.name, pdf_content)
        else:
            messages.error(request, "Hubo un error al generar el PDF del certificado. Verifique la configuración del servidor.")
            return redirect('capacitaciones:mis_capacitaciones')
            
    # Return PDF using Django File storage
    try:
        response = HttpResponse(inscripcion.certificado.read(), content_type='application/pdf')
        filename = os.path.basename(inscripcion.certificado.name)
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
    except Exception as e:
        messages.error(request, f"Error al leer el archivo del certificado: {str(e)}")
        return redirect('capacitaciones:mis_capacitaciones')
