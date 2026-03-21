from django.shortcuts import render
from django.http import JsonResponse
from .models import SubrubroFeriante

def ajax_get_subrubros(request):
    rubro_id = request.GET.get('rubro_id')
    if rubro_id:
        subrubros = SubrubroFeriante.objects.filter(rubro_id=rubro_id).order_by('nombre')
        data = [{'id': s.id_subrubro, 'nombre': s.nombre} for s in subrubros]
    else:
        data = []
    return JsonResponse(data, safe=False)
