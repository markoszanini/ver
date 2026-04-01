from django.http import JsonResponse
from django.db.models import Q
from .models import Direccion, Departamento, Division, Subdivision, Seccion, Oficina

def get_direcciones(request):
    area_id = request.GET.get('area_id')
    if not area_id:
        return JsonResponse({'results': []})
    qs = Direccion.objects.filter(area_id=area_id)
    return JsonResponse({'results': [{'id': q.pk, 'text': q.nombre} for q in qs]})

def get_departamentos(request):
    area_id = request.GET.get('area_id')
    dir_id = request.GET.get('dir_id')
    
    if dir_id:
        qs = Departamento.objects.filter(direccion_id=dir_id)
    elif area_id:
        # Mostramos todos los deptos del área si no hay dirección seleccionada
        qs = Departamento.objects.filter(area_id=area_id)
    else:
        qs = Departamento.objects.none()
        
    return JsonResponse({'results': [{'id': q.pk, 'text': q.nombre} for q in qs]})

def get_divisiones(request):
    area_id = request.GET.get('area_id')
    if area_id == '24':
        return JsonResponse({'results': []})
    depto_id = request.GET.get('depto_id')
    if not depto_id:
        return JsonResponse({'results': []})
    qs = Division.objects.filter(departamento_id=depto_id)
    return JsonResponse({'results': [{'id': q.pk, 'text': q.nombre} for q in qs]})

def get_subdivisiones(request):
    area_id = request.GET.get('area_id')
    if area_id == '24':
        return JsonResponse({'results': []})
    depto_id = request.GET.get('depto_id')
    div_id = request.GET.get('div_id')
    dir_id = request.GET.get('dir_id')

    # REGLA ESPECIAL AREA 23: Taxis y Remises solo si SOLO esta seleccionada el área.
    if area_id == '23' and not dir_id and not depto_id:
        qs = Subdivision.objects.filter(area_id=area_id, departamento_id__isnull=True, division_id__isnull=True)
        return JsonResponse({'results': [{'id': q.pk, 'text': q.nombre} for q in qs]})
    
    # Para el resto (o si hay dir/depto en 23), filtramos por los padres normales.
    if div_id:
        qs = Subdivision.objects.filter(division_id=div_id)
    elif depto_id:
        qs = Subdivision.objects.filter(departamento_id=depto_id)
    else:
        return JsonResponse({'results': []})
    return JsonResponse({'results': [{'id': q.pk, 'text': q.nombre} for q in qs]})

def get_secciones(request):
    area_id = request.GET.get('area_id')
    if area_id == '24':
        return JsonResponse({'results': []})
    depto_id = request.GET.get('depto_id')
    subdiv_id = request.GET.get('subdiv_id')
    div_id = request.GET.get('div_id')
    dir_id = request.GET.get('dir_id')
    
    # REGLA ESPECIAL AREA 23: Mayordomía es la UNICA sección y solo de nivel área.
    if area_id == '23':
        if not dir_id and not depto_id:
            qs = Seccion.objects.filter(area_id=area_id, departamento_id__isnull=True, subdivision_id__isnull=True)
            return JsonResponse({'results': [{'id': q.pk, 'text': q.nombre} for q in qs]})
        else:
            # Según usuario: "las demás no pertenecen a esa área".
            return JsonResponse({'results': []})

    # REGLA ESPECIAL: Si es Mantenimiento y Producción (ID 3 o 29) y hay una división seleccionada, ocultamos secciones.
    if depto_id in ['3', '29'] and div_id:
        return JsonResponse({'results': []})

    if subdiv_id:
        qs = Seccion.objects.filter(subdivision_id=subdiv_id)
    elif depto_id:
        qs = Seccion.objects.filter(departamento_id=depto_id)
    else:
        return JsonResponse({'results': []})
    return JsonResponse({'results': [{'id': q.pk, 'text': q.nombre} for q in qs]})

def get_oficinas(request):
    area_id = request.GET.get('area_id')
    dir_id = request.GET.get('dir_id')
    depto_id = request.GET.get('depto_id')
    div_id = request.GET.get('div_id')
    subdiv_id = request.GET.get('subdiv_id')
    sec_id = request.GET.get('sec_id')
    
    # REGLAS PARA AREAS DE GOBIERNO (23): 
    # Si no hay depto, mostrar solo las de nivel area (depto_id=None).
    # Si hay depto, mostrar solo las de ese depto.
    if area_id == '23':
        if not depto_id:
            qs = Oficina.objects.filter(area_id=area_id, departamento_id__isnull=True)
        else:
            qs = Oficina.objects.filter(area_id=area_id, departamento_id=depto_id)
        return JsonResponse({'results': [{'id': q.pk, 'text': q.nombre} for q in qs]})

    # REGLA ESTRICTA AREA DE PRODUCCION (24): Requiere depto.
    if area_id == '24':
        if not depto_id:
            return JsonResponse({'results': []})
        qs = Oficina.objects.filter(area_id=area_id, departamento_id=depto_id)
        return JsonResponse({'results': [{'id': q.pk, 'text': q.nombre} for q in qs]})

    if sec_id:
        qs = Oficina.objects.filter(seccion_id=sec_id)
    elif subdiv_id:
        qs = Oficina.objects.filter(subdivision_id=subdiv_id)
    elif div_id:
        qs = Oficina.objects.filter(division_id=div_id)
    elif depto_id:
        qs = Oficina.objects.filter(departamento_id=depto_id)
    elif dir_id:
        qs = Oficina.objects.filter(direccion_id=dir_id)
    elif area_id:
        qs = Oficina.objects.filter(area_id=area_id)
    else:
        qs = Oficina.objects.none()
        
    return JsonResponse({'results': [{'id': q.pk, 'text': q.nombre} for q in qs]})
