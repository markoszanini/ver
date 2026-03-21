from django.shortcuts import render
from django.db.models import Q
from datetime import date
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from .models import Postulante, RubroEmpleo, Idioma, PuestoEmpleo

@staff_member_required
def perfiles_cv(request):
    qs = Postulante.objects.none()
    
    edad_desde = request.GET.get('edad_desde')
    edad_hasta = request.GET.get('edad_hasta')
    sexo = request.GET.get('sexo')
    localidad = request.GET.get('localidad')
    rubro = request.GET.get('rubro')
    movilidad = request.GET.get('movilidad')
    viajar = request.GET.get('viajar')
    idioma = request.GET.get('idioma')
    nivel_estudio = request.GET.get('nivel_estudio')
    puesto = request.GET.get('puesto')

    has_filters = any([edad_desde, edad_hasta, sexo, localidad, rubro, movilidad, viajar, idioma, nivel_estudio, puesto])

    if has_filters:
        qs = Postulante.objects.all()

        if edad_desde:
            try:
                max_date = date.today().replace(year=date.today().year - int(edad_desde))
                qs = qs.filter(fecha_nac__lte=max_date)
            except: pass
            
        if edad_hasta:
            try:
                min_date = date.today().replace(year=date.today().year - int(edad_hasta) - 1)
                qs = qs.filter(fecha_nac__gt=min_date)
            except: pass

        if sexo: qs = qs.filter(sexo__iexact=sexo)
        if localidad: qs = qs.filter(localidad=localidad)
        if rubro: qs = qs.filter(postulaciones__rubro_id=rubro)
        if movilidad: qs = qs.filter(movilidad_propia=movilidad)
        if viajar: qs = qs.filter(disponibilidad_viajar=viajar)
        if idioma: qs = qs.filter(idiomas__idioma=idioma)
        if nivel_estudio: qs = qs.filter(estudios__nivel__icontains=nivel_estudio)
        if puesto: qs = qs.filter(postulaciones__puesto__icontains=puesto)

        qs = qs.distinct().order_by('apellido', 'nombre')

    rubros = RubroEmpleo.objects.filter(activo='S').order_by('descripcion')
    idiomas = sorted(Idioma.IDIOMA_CHOICES, key=lambda x: x[1])
    localidades = sorted(Postulante.LOCALIDAD_CHOICES, key=lambda x: x[1] if x[0] != '8' else 'zzzzz') # Sort alphabetically except 'Otro'
    
    resultados = []
    for p in qs:
        edad = ''
        if p.fecha_nac:
            today = date.today()
            edad = today.year - p.fecha_nac.year - ((today.month, today.day) < (p.fecha_nac.month, p.fecha_nac.day))
        
        resultados.append({
            'postulante': p,
            'dni': p.vecino.dni if p.vecino else ('N/A - ID: ' + str(p.id_postulante)),
            'edad': edad,
            'telefono': p.telefono,
            'mail': p.mail,
            'estudios': ", ".join([e.nivel for e in p.estudios.all() if e.nivel])
        })

    context = {
        'has_filters': has_filters,
        'resultados': resultados,
        'rubros': rubros,
        'idiomas': idiomas,
        'localidades': localidades,
        'filtros': request.GET,
    }
    
    return render(request, 'empleo/perfiles_cv.html', context)

@staff_member_required
def ajax_get_puestos(request):
    rubro_id = request.GET.get('rubro_id')
    if rubro_id:
        puestos = PuestoEmpleo.objects.filter(rubro_id=rubro_id, activo='S').order_by('descripcion').values('id_puesto', 'descripcion')
        return JsonResponse(list(puestos), safe=False)
    return JsonResponse([], safe=False)

