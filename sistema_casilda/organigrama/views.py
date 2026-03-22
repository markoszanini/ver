from django.http import JsonResponse
from django.db.models import Q
from .models import Direccion, Departamento, Division, Subdivision, Seccion, Oficina

def get_direcciones(request):
    area_id = request.GET.get('area_id')
    qs = Direccion.objects.filter(area_id=area_id) if area_id else Direccion.objects.none()
    return JsonResponse({'results': [{'id': q.pk, 'text': q.nombre} for q in qs]})

def get_departamentos(request):
    area_id = request.GET.get('area_id') or None
    dir_id = request.GET.get('dir_id') or None
    
    if not area_id and not dir_id:
        qs = Departamento.objects.none()
    else:
        query = Q()
        if dir_id:
            query |= Q(direccion_id__isnull=False, direccion_id=dir_id)
        if area_id and not dir_id:
            query |= Q(direccion_id__isnull=True, area_id=area_id)
            
        qs = Departamento.objects.filter(query) if query else Departamento.objects.none()
        
    return JsonResponse({'results': [{'id': q.pk, 'text': q.nombre} for q in qs]})

def get_divisiones(request):
    depto_id = request.GET.get('depto_id')
    qs = Division.objects.filter(departamento_id=depto_id) if depto_id else Division.objects.none()
    return JsonResponse({'results': [{'id': q.pk, 'text': q.nombre} for q in qs]})

def get_subdivisiones(request):
    depto_id = request.GET.get('depto_id')
    qs = Subdivision.objects.filter(departamento_id=depto_id) if depto_id else Subdivision.objects.none()
    return JsonResponse({'results': [{'id': q.pk, 'text': q.nombre} for q in qs]})

def get_secciones(request):
    depto_id = request.GET.get('depto_id') or None
    subdiv_id = request.GET.get('subdiv_id') or None
    
    if not depto_id and not subdiv_id:
        qs = Seccion.objects.none()
    else:
        query = Q()
        if depto_id:
            query |= Q(departamento_id=depto_id)
        if subdiv_id:
            query |= Q(subdivision_id=subdiv_id)
        qs = Seccion.objects.filter(query)
        
    return JsonResponse({'results': [{'id': q.pk, 'text': q.nombre} for q in qs]})

def get_oficinas(request):
    area_id = request.GET.get('area_id') or None
    dir_id = request.GET.get('dir_id') or None
    depto_id = request.GET.get('depto_id') or None
    div_id = request.GET.get('div_id') or None
    subdiv_id = request.GET.get('subdiv_id') or None
    sec_id = request.GET.get('sec_id') or None
    
    if area_id and not any([dir_id, depto_id, div_id, subdiv_id, sec_id]):
        qs = Oficina.objects.filter(area_id=area_id)
    else:
        qs = Oficina.objects.none()
        
    return JsonResponse({'results': [{'id': q.pk, 'text': q.nombre} for q in qs]})
