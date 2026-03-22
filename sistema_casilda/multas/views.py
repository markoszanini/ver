from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Q
from .models import Acta, Persona, Vehiculo, Inmueble
from django.utils import timezone

def index_consultas(request):
    """Vista inicial estílo APEX con las 4 tarjetas de opciones principales."""
    return render(request, 'multas/index_consultas.html')

def consulta_publica(request, tipo_consulta='general'):
    """Vista principal para consultar multas por el vecino."""
    resultados = None
    busqueda_realizada = False
    parametro = ""

    if request.method == 'POST':
        dni = request.POST.get('dni', '').strip()
        patente = request.POST.get('patente', '').strip()
        nomenclatura = request.POST.get('nomenclatura', '').strip()
        busqueda_realizada = True

        filtros = Q()
        if dni:
            filtros |= Q(persona__dni=dni)
            parametro = f"DNI: {dni}"
        if patente:
            filtros |= Q(vehiculo__patente=patente)
            parametro = f"Patente: {patente}"
        if nomenclatura:
            filtros |= Q(inmueble__nomenclatura=nomenclatura)
            parametro = f"Nomenclatura: {nomenclatura}"

        if filtros:
            # Solo mostramos multas pendientes
            resultados = Acta.objects.filter(filtros, estado='PENDIENTE').select_related('persona', 'vehiculo', 'inmueble', 'motivo')

    context = {
        'resultados': resultados,
        'busqueda_realizada': busqueda_realizada,
        'parametro': parametro,
        'tipo_consulta': tipo_consulta,
    }
    return render(request, 'multas/consulta_publica.html', context)


def libre_deuda_pdf(request):
    """Genera el certificado de Libre de Multas."""
    parametro = request.GET.get('parametro', 'Desconocido')
    
    # Por ahora renderizamos un HTML, si hay librería PDF lo convertimos
    context = {
        'parametro': parametro,
        'fecha': timezone.now(),
    }
    return render(request, 'multas/libre_deuda.html', context)


def acta_pdf(request, id_acta):
    """Genera el PDF de una multa específica."""
    acta = get_object_or_404(Acta, pk=id_acta)
    
    context = {
        'acta': acta,
        'fecha': timezone.now(),
    }
    return render(request, 'multas/acta_detalle.html', context)


def pagar_acta(request, id_acta):
    """Simula una pasarela de pagos."""
    acta = get_object_or_404(Acta, pk=id_acta)
    if request.method == 'POST':
        # Simular pago exitoso
        acta.estado = 'PAGADA'
        acta.save()
        return redirect('multas:consulta_publica')

    return render(request, 'multas/pagar_acta.html', {'acta': acta})
