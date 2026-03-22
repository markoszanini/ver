from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta, date

from .models import Turno, ConfiguracionTurno

@login_required
def mis_turnos(request):
    if not hasattr(request.user, 'vecino_profile'):
        return redirect('portal:home')
    
    vecino = request.user.vecino_profile
    turnos = Turno.objects.filter(vecino=vecino).order_by('-fecha', '-hora')
    return render(request, 'turnos/mis_turnos.html', {'turnos': turnos})

@login_required
def solicitar_turno(request):
    if not hasattr(request.user, 'vecino_profile'):
        return redirect('portal:home')
    
    if request.method == 'POST':
        tipo_turno = request.POST.get('tipo_turno')
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora')
        
        try:
            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            if fecha_obj < date.today():
                messages.error(request, "No puede solicitar turnos en fechas pasadas.")
                return redirect('turnos:solicitar_turno')
                
            hora_obj = datetime.strptime(hora_str, '%H:%M').time()
            
            # Validación con Configuración
            config = ConfiguracionTurno.objects.filter(tipo_turno=tipo_turno).first()
            if not config:
                messages.error(request, "Este tipo de turno no está disponible porque la municipalidad aún no programó la agenda.")
                return redirect('turnos:solicitar_turno')

            # Verificar si ya existe el turno y "ganó" otro usuario
            if Turno.objects.filter(tipo_turno=tipo_turno, fecha=fecha_obj, hora=hora_obj).exists():
                messages.error(request, "Lo sentimos, el horario que seleccionaste recién fue reservado por otra persona. Por favor elige otro.")
                return redirect('turnos:solicitar_turno')

            # Armar kwargs
            kwargs = {
                'vecino': request.user.vecino_profile,
                'tipo_turno': tipo_turno,
                'fecha': fecha_obj,
                'hora': hora_obj,
                'estado': 'PENDIENTE'
            }
            
            if tipo_turno == 'LICENCIA':
                kwargs['tipo_licencia'] = request.POST.get('tipo_licencia')
                vencimiento_str = request.POST.get('vencimiento_licencia')
                if not vencimiento_str:
                    messages.error(request, "Debe brindar la fecha de vencimiento de su licencia actual.")
                    return redirect('turnos:solicitar_turno')
                kwargs['vencimiento_licencia'] = datetime.strptime(vencimiento_str, '%Y-%m-%d').date()

            Turno.objects.create(**kwargs)
            messages.success(request, f"Tu turno para {Turno(tipo_turno=tipo_turno).get_tipo_turno_display()} fue reservado exitosamente.")
            return redirect('turnos:mis_turnos')
            
        except Exception as e:
            messages.error(request, f"Error al procesar el turno: Verifique los datos ingresados.")
            return redirect('turnos:solicitar_turno')

    return render(request, 'turnos/solicitar_turno.html')

@login_required
def api_horarios_disponibles(request):
    fecha_str = request.GET.get('fecha')
    tipo = request.GET.get('tipo')
    
    if not fecha_str or not tipo:
        return JsonResponse({'error': 'Parámetros insuficientes'}, status=400)
        
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        config = ConfiguracionTurno.objects.filter(tipo_turno=tipo).first()
        if not config:
            return JsonResponse({'horarios': [], 'mensaje': f'El área encargada aún no definió la agenda para {tipo}.'})
            
        dias_validos = [int(d) for d in config.dias_habiles.split(',')]
        if fecha.weekday() not in dias_validos:
            return JsonResponse({'horarios': [], 'mensaje': 'El establecimiento no atiende los días seleccionados.'})
            
        hoy = date.today()
        if fecha < hoy:
             return JsonResponse({'horarios': [], 'mensaje': 'No puede solicitar fechas en el pasado.'})
             
        # Calcular franjas
        base_date = datetime(2000, 1, 1)
        start_dt = datetime.combine(base_date, config.hora_inicio)
        end_dt = datetime.combine(base_date, config.hora_fin)
        
        minutes_per_turn = 60 // config.turnos_por_hora
        
        horarios = []
        current = start_dt
        while current < end_dt:
            horarios.append(current.time())
            current += timedelta(minutes=minutes_per_turn)
            
        # Excluir horarios ya reservados ese mismo día
        existentes = Turno.objects.filter(tipo_turno=tipo, fecha=fecha).values_list('hora', flat=True)
        
        disponibles = []
        for h in horarios:
            if h not in existentes:
                # Si es hoy, excluir los que ya se pasaron de hora
                if fecha > hoy or (fecha == hoy and h > datetime.now().time()):
                    disponibles.append(h.strftime('%H:%M'))
                
        if not disponibles:
             return JsonResponse({'horarios': [], 'mensaje': 'Todos los turnos para esta fecha han sido ocupados.'})
             
        return JsonResponse({'horarios': disponibles})
    except Exception as e:
         return JsonResponse({'error': str(e)}, status=500)
