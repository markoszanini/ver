from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from organigrama.models import Area, Direccion, Departamento, Division, Subdivision, Seccion, Oficina
from django.db.models import Q

@login_required
def buscar_destinos_ajax(request):
    query = request.GET.get('q', '').strip()
    if not query or len(query) < 2:
        return JsonResponse({'results': []})

    results = []
    
    # 1. Áreas
    for obj in Area.objects.filter(nombre__icontains=query)[:5]:
        results.append({'id': f'area_{obj.pk}', 'text': f"{obj.nombre} (Área)"})
        
    # 2. Direcciones
    for obj in Direccion.objects.filter(nombre__icontains=query)[:5]:
        results.append({'id': f'direccion_{obj.pk}', 'text': f"{obj.nombre} (Dirección)"})
        
    # 3. Departamentos
    for obj in Departamento.objects.filter(nombre__icontains=query)[:5]:
        results.append({'id': f'departamento_{obj.pk}', 'text': f"{obj.nombre} (Departamento)"})
        
    # 4. Divisiones
    for obj in Division.objects.filter(nombre__icontains=query)[:5]:
        results.append({'id': f'division_{obj.pk}', 'text': f"{obj.nombre} (División)"})
        
    # 5. Subdivisiones
    for obj in Subdivision.objects.filter(nombre__icontains=query)[:5]:
        results.append({'id': f'subdivision_{obj.pk}', 'text': f"{obj.nombre} (Subdivisión)"})
        
    # 6. Secciones
    for obj in Seccion.objects.filter(nombre__icontains=query)[:5]:
        results.append({'id': f'seccion_{obj.pk}', 'text': f"{obj.nombre} (Sección)"})
        
    # 7. Oficinas
    for obj in Oficina.objects.filter(nombre__icontains=query)[:10]:
        results.append({'id': f'oficina_{obj.pk}', 'text': f"{obj.nombre} (Oficina)"})

    return JsonResponse({'results': results})
