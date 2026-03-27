from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import models
from django.db.models import Q
from .models import ReciboSueldo, Vacaciones, NovedadRRHH
from organigrama.models import Funcionario

def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def portal_empleado(request):
    try:
        funcionario = request.user.funcionario_link
    except Funcionario.DoesNotExist:
        messages.error(request, "No tienes un perfil de funcionario asignado. Contacta a RRHH.")
        return redirect('portal:dashboard')

    recibos_recientes = ReciboSueldo.objects.filter(funcionario=funcionario).order_by('-anio', '-mes')[:3]
    vacaciones = getattr(funcionario, 'vacaciones', None)
    novedades = NovedadRRHH.objects.filter(
        Q(es_general=True) | Q(funcionario_destino=funcionario)
    ).order_by('-fecha')[:5]

    # Lógica para ver si es Jefe de RRHH (Gobierno y Gestión [ID 23] -> Dep. Personal [ID 1])
    # También incluimos por nombre como fallback.
    puede_gestionar_rrhh = False
    if funcionario.rango == 'JEFE' or funcionario.usuario_login == 'tiago.bernardis':
        area_id = funcionario.area_id
        depto_id = funcionario.departamento_id
        area_nom = funcionario.area.nombre.lower() if funcionario.area else ""
        dep_nom = funcionario.departamento.nombre.lower() if funcionario.departamento else ""
        
        # Acceso por ID (más robusto) o por nombre
        if (area_id == 23 and depto_id == 1) or ('gobierno' in area_nom and 'personal' in dep_nom):
            puede_gestionar_rrhh = True

    return render(request, 'recursos_humanos/portal.html', {
        'funcionario': funcionario,
        'recibos': recibos_recientes,
        'vacaciones': vacaciones,
        'novedades': novedades,
        'puede_gestionar_rrhh': puede_gestionar_rrhh,
    })

@login_required
@user_passes_test(is_staff)
def mis_recibos(request):
    funcionario = request.user.funcionario_link
    recibos = ReciboSueldo.objects.filter(funcionario=funcionario).order_by('-anio', '-mes')
    return render(request, 'recursos_humanos/recibos.html', {'recibos': recibos})

@login_required
@user_passes_test(is_staff)
def mis_vacaciones(request):
    funcionario = request.user.funcionario_link
    vacaciones = getattr(funcionario, 'vacaciones', None)
    return render(request, 'recursos_humanos/vacaciones.html', {'vacaciones': vacaciones})
