from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Expediente, MovimientoExpediente, NotificacionExpediente
from .forms import ExpedienteInternalForm, PaseExpedienteForm, ExpedienteMesaForm, ConfirmarExpedienteMesaForm
from organigrama.models import Funcionario, Departamento, Oficina, Area, Direccion, RangoEmpleado
from django.db.models import Q

@login_required
def mis_expedientes(request):
    vecino = getattr(request.user, 'vecino_profile', None)
    if not vecino:
        # Si es staff, tal vez quiera ver sus expedientes internos creados
        return redirect('expedientes:mis_expedientes_internos')
    
    expedientes = Expediente.objects.filter(vecino_titular=vecino).order_by('-fecha_ingreso')
    return render(request, 'expedientes/mis_expedientes.html', {'expedientes': expedientes})

@login_required
def mis_expedientes_internos(request):
    funcionario = getattr(request.user, 'funcionario_link', None)
    if not funcionario:
        return redirect('home')
        
    # LOGICA UNIFICADA: 
    # 1. BANDEJA (Pendientes de Acción): Lo que está físicamente aquí.
    # 2. TODOS (Seguimiento): Lo iniciado aquí + lo que está físicamente aquí.
    
    # Origen: ¿Se inició en esta oficina/área?
    origen_q = Q()
    if funcionario.oficina:
        origen_q = Q(origen_oficina=funcionario.oficina)
    elif funcionario.departamento:
        origen_q = Q(origen_departamento=funcionario.departamento)
    elif funcionario.direccion:
        origen_q = Q(origen_direccion=funcionario.direccion)
    elif funcionario.area:
        origen_q = Q(origen_area=funcionario.area)
        
    # Ubicación Actual: ¿Está aquí ahora mismo?
    location_q = Q()
    if funcionario.oficina:
        location_q = Q(actual_oficina=funcionario.oficina)
    elif funcionario.departamento:
        location_q = Q(actual_departamento=funcionario.departamento)
    elif funcionario.direccion:
        location_q = Q(actual_direccion=funcionario.direccion)
    elif funcionario.area:
        location_q = Q(actual_area=funcionario.area)
        
    # Query 1: Pendientes de acción (Bandeja)
    pendientes = Expediente.objects.filter(location_q, confirmado=True).exclude(estado__in=['Resuelto', 'Archivado', 'Finalizado']).order_by('-visto', '-fecha_ingreso')
    
    # Query 2: Todos los de la oficina (Historial/Seguimiento)
    todos = Expediente.objects.filter(
        (origen_q) | (location_q & Q(confirmado=True))
    ).exclude(estado__in=['Resuelto', 'Archivado', 'Finalizado']).order_by('-fecha_ingreso').distinct()
    
    return render(request, 'expedientes/mis_expedientes_internos.html', {
        'pendientes': pendientes,
        'todos': todos,
        'funcionario': funcionario,
        'active_tab': request.GET.get('tab', 'bandeja' if pendientes.exists() else 'todos')
    })



@login_required
def iniciar_expediente_staff(request):
    funcionario = getattr(request.user, 'funcionario_link', None)
    if not funcionario:
        messages.error(request, "Solo personal municipal puede iniciar expedientes internos.")
        return redirect('home')

    # Solo Jefes o Secretarios (o Superusers) pueden iniciar
    from organigrama.models import RangoEmpleado
    if funcionario.rango not in [RangoEmpleado.JEFE, RangoEmpleado.SECRETARIO] and not request.user.is_superuser:
        messages.error(request, "No tiene permisos de rango (Jefe/Secretario) para iniciar expedientes.")
        return redirect('home')

    # No debe ser de Mesa de Entrada (ellos usan el Admin estándar para carga directa)
    if funcionario.departamento and 'mesa de entrada' in funcionario.departamento.nombre.lower():
        messages.warning(request, "Como personal de Mesa de Entradas, use el Panel Administrativo para cargar expedientes directamente.")
        return redirect('/admin/expedientes/expediente/add/')

    if request.method == 'POST':
        form = ExpedienteInternalForm(request.POST, request.FILES)
        if form.is_valid():
            expediente = form.save(commit=False)
            expediente.creado_por = request.user
            expediente.solicitante_interno = funcionario
            expediente.origen_area = funcionario.area
            expediente.origen_departamento = funcionario.departamento
            expediente.origen_direccion = funcionario.direccion
            expediente.origen_oficina = funcionario.oficina
            
            # Destino inicial: Mesa de Entradas para confirmación
            mesa = Departamento.objects.filter(nombre__icontains='mesa de entrada').first()
            if mesa:
                expediente.actual_departamento = mesa
                expediente.actual_area = mesa.direccion.area if mesa.direccion else None
            
            expediente.confirmado = False
            expediente.estado = 'Pendiente de Confirmación'
            expediente.save()
            
            # Notificar a Mesa de Entradas
            from organigrama.models import Funcionario, RangoEmpleado
            destinatarios_mesa = Funcionario.objects.filter(
                departamento__nombre__icontains='mesa de entrada',
                rango__in=[RangoEmpleado.JEFE, RangoEmpleado.SECRETARIO]
            )
            for fm in destinatarios_mesa:
                if fm.user:
                    NotificacionExpediente.objects.create(
                        usuario=fm.user,
                        expediente=expediente,
                        mensaje=f"Nuevo expediente interno esperando número: {expediente.asunto[:40]}..."
                    )
            
            messages.success(request, f"Expediente iniciado correctamente. Mesa de Entrada ha sido notificada para el foliado.")
            return redirect('expedientes:mis_expedientes_internos')

    else:
        form = ExpedienteInternalForm()

    return render(request, 'expedientes/iniciar_expediente.html', {
        'form': form,
        'funcionario': funcionario
    })

@login_required
def seguimiento_expediente(request, id_expediente):
    vecino = getattr(request.user, 'vecino_profile', None)
    funcionario = getattr(request.user, 'funcionario_link', None)
    
    from django.db.models import Q
    expediente = get_object_or_404(Expediente, id_expediente=id_expediente)
    
    # Verificación de permisos
    allowed = False
    if request.user.is_superuser:
        allowed = True
    elif vecino and expediente.vecino_titular == vecino:
        allowed = True
    elif funcionario:
        # El funcionario puede verlo si es el creador/solicitante, o si el expediente está en su área
        if expediente.creado_por == request.user or expediente.solicitante_interno == funcionario:
            allowed = True
        elif (expediente.actual_area == funcionario.area or 
              expediente.actual_departamento == funcionario.departamento or 
              expediente.actual_oficina == funcionario.oficina):
            allowed = True
            
    if not allowed:
        messages.error(request, "No tiene permisos para ver el seguimiento de este expediente.")
        return redirect('home')
        
    movimientos = expediente.movimientos.all().order_by('fecha_pase') 
    
    return render(request, 'expedientes/seguimiento.html', {
        'expediente': expediente,
        'movimientos': movimientos
    })

@login_required
def bandeja_entrada(request):
    return redirect(f"/expedientes/mis-expedientes-internos/?tab=bandeja")


@login_required
def procesar_expediente(request, id_expediente):
    funcionario = getattr(request.user, 'funcionario_link', None)
    expediente = get_object_or_404(Expediente, id_expediente=id_expediente)

    # Permisos: Solo si está en su oficina y es Jefe/Secretario
    is_at_location = False
    if funcionario:
        if (expediente.actual_oficina == funcionario.oficina and funcionario.oficina) or \
           (expediente.actual_departamento == funcionario.departamento and funcionario.departamento) or \
           (expediente.actual_direccion == funcionario.direccion and funcionario.direccion) or \
           (expediente.actual_area == funcionario.area and funcionario.area):
            is_at_location = True

    if not is_at_location and not request.user.is_superuser:
        messages.error(request, "No tiene permisos para procesar este expediente.")
        return redirect('expedientes:bandeja_entrada')

    if funcionario.rango not in [RangoEmpleado.JEFE, RangoEmpleado.SECRETARIO] and not request.user.is_superuser:
        messages.error(request, "Solo Jefes o Secretarios pueden realizar pases.")
        return redirect('expedientes:seguimiento_expediente', id_expediente=id_expediente)

    # Marcar como visto si no lo estaba
    if not expediente.visto:
        expediente.visto = True
        expediente.save(update_fields=['visto'])
        # Marcar notificaciones relacionadas como leídas
        NotificacionExpediente.objects.filter(usuario=request.user, expediente=expediente, leido=False).update(leido=True)

    if request.method == 'POST':
        # 1. Guardar Resolución Actual
        resolucion_texto = request.POST.get('resolucion_provisoria', '')
        expediente.ultima_resolucion = resolucion_texto
        expediente.save(update_fields=['ultima_resolucion'])
        
        # 2. Procesar Pase si se envió
        if 'realizar_pase' in request.POST:
            form_pase = PaseExpedienteForm(request.POST)
            if form_pase.is_valid():
                # Crear Movimiento
                mov = MovimientoExpediente.objects.create(
                    expediente=expediente,
                    destino_area=form_pase.cleaned_data.get('destino_area'),
                    destino_direccion=form_pase.cleaned_data.get('destino_direccion'),
                    destino_departamento=form_pase.cleaned_data.get('destino_departamento'),
                    destino_oficina=form_pase.cleaned_data.get('destino_oficina'),
                    observacion=form_pase.cleaned_data.get('observacion_pase'),
                    usuario_emisor=f"{funcionario.apellido}, {funcionario.nombre}",
                    resolucion=expediente.ultima_resolucion,
                    estado='En Pase'
                )
                
                # Actualizar Expediente
                expediente.actual_area = mov.destino_area
                expediente.actual_direccion = mov.destino_direccion
                expediente.actual_departamento = mov.destino_departamento
                expediente.actual_oficina = mov.destino_oficina
                expediente.visto = False
                expediente.estado = 'En trámite'
                expediente.save()

                # Generar Notificaciones para los Jefes/Secretarios del destino
                generar_notificaciones_destino(expediente, mov)

                messages.success(request, f"Pase realizado correctamente. El expediente ahora se encuentra en {expediente.ubicacion_display}")
                return redirect('expedientes:bandeja_entrada')
        
        # 3. Archivar si es de Mesa y se pidió
        if 'archivar' in request.POST:
            if funcionario.departamento and 'mesa de entrada' in funcionario.departamento.nombre.lower():
                expediente.estado = 'Resuelto/Archivado'
                expediente.fecha_salida = import_datetime().date()
                expediente.save()
                messages.success(request, "Expediente finalizado y archivado correctamente.")
                return redirect('expedientes:bandeja_entrada')
            else:
                messages.error(request, "Solo Mesa de Entradas puede dar por finalizado un expediente.")

    form_pase = PaseExpedienteForm()
    movimientos = expediente.movimientos.all().order_by('fecha_pase')

    return render(request, 'expedientes/procesar_expediente.html', {
        'expediente': expediente,
        'form_pase': form_pase,
        'movimientos': movimientos,
        'funcionario': funcionario
    })

def generar_notificaciones_destino(expediente, movimiento):
    # Buscar funcionarios en el destino EXACTO con rango Jefe/Secretario
    # OJO: Si se envió a una Oficina, solo buscamos gente en esa Oficina.
    # Si se envió a un Área general, buscamos gente en ese Área.
    filters = Q()
    if movimiento.destino_oficina:
        filters = Q(oficina=movimiento.destino_oficina)
    elif movimiento.destino_departamento:
        filters = Q(departamento=movimiento.destino_departamento)
    elif movimiento.destino_direccion:
        filters = Q(direccion=movimiento.destino_direccion)
    elif movimiento.destino_area:
        filters = Q(area=movimiento.destino_area)

    if filters == Q():
        return # No hay destino definido

    destinatarios = Funcionario.objects.filter(
        filters,
        rango__in=[RangoEmpleado.JEFE, RangoEmpleado.SECRETARIO]
    ).distinct()

    for func in destinatarios:
        if func.user:
            NotificacionExpediente.objects.create(
                usuario=func.user,
                expediente=expediente,
                mensaje=f"Nuevo expediente en su oficina: {expediente.nro_expediente or 'S/N'}."
            )


@login_required
def mesa_dashboard(request):
    funcionario = getattr(request.user, 'funcionario_link', None)
    if not funcionario or not (funcionario.departamento and 'mesa' in funcionario.departamento.nombre.lower()):
        messages.error(request, "Acceso exclusivo para personal de Mesa de Entradas.")
        return redirect('portal:dashboard')

    q = request.GET.get('q', '')
    
    # 1. Por Confirmar: Expedientes iniciados por staff que no tienen número aún
    por_confirmar = Expediente.objects.filter(confirmado=False)
    
    # 2. Control Global de seguimiento (Todo lo que no esté archivado/resueltos)
    en_tramite = Expediente.objects.filter(confirmado=True).exclude(estado__in=['Resuelto', 'Archivado', 'Finalizado'])

    if q:
        query = Q(nro_expediente__icontains=q) | \
                Q(asunto__icontains=q) | \
                Q(dni_titular_manual__icontains=q) | \
                Q(vecino_titular__dni__icontains=q) | \
                Q(nombre_titular_manual__icontains=q) | \
                Q(apellido_titular_manual__icontains=q) | \
                Q(solicitante_interno__nombre__icontains=q) | \
                Q(solicitante_interno__apellido__icontains=q) | \
                Q(origen_oficina__nombre__icontains=q) | \
                Q(origen_departamento__nombre__icontains=q)
        
        por_confirmar = por_confirmar.filter(query)
        en_tramite = en_tramite.filter(query)

    por_confirmar = por_confirmar.order_by('-fecha_ingreso')
    en_tramite = en_tramite.order_by('-fecha_ingreso')

    return render(request, 'expedientes/mesa_dashboard.html', {
        'por_confirmar': por_confirmar,
        'en_tramite': en_tramite,
        'funcionario': funcionario,
        'q': q
    })

@login_required
def crear_expediente_mesa(request):
    funcionario = getattr(request.user, 'funcionario_link', None)
    if not funcionario or not (funcionario.departamento and 'mesa' in funcionario.departamento.nombre.lower()):
        return redirect('portal:dashboard')

    if request.method == 'POST':
        form = ExpedienteMesaForm(request.POST, request.FILES)
        if form.is_valid():
            expediente = form.save(commit=False)
            expediente.creado_por = request.user
            expediente.registrado_por = f"{funcionario.apellido}, {funcionario.nombre}"
            
            # Al ser creado por Mesa, podemos confirmarlo inmediatamente si tiene destino
            expediente.confirmado = True
            expediente.estado = 'En trámite'
            
            # El número se genera en el save() del modelo al detectar confirmado=True
            expediente.save()
            
            # Movimiento inicial (Mesa -> Destino sugerido)
            destino = form.cleaned_data.get('oficina_destino_sugerida')
            if destino:
                expediente.actual_oficina = destino
                expediente.actual_departamento = destino.departamento
                expediente.actual_direccion = destino.departamento.direccion if destino.departamento else None
                expediente.actual_area = destino.departamento.direccion.area if (destino.departamento and destino.departamento.direccion) else None
                expediente.save()
                
                mov = MovimientoExpediente.objects.create(
                    expediente=expediente,
                    destino_oficina=destino,
                    destino_departamento=expediente.actual_departamento,
                    destino_direccion=expediente.actual_direccion,
                    destino_area=expediente.actual_area,
                    usuario_emisor=expediente.registrado_por,
                    observacion="Expediente iniciado y numerado por Mesa de Entradas.",
                    estado='Iniciado'
                )
                generar_notificaciones_destino(expediente, mov)

            messages.success(request, f"Expediente {expediente.nro_expediente} creado y numerado correctamente.")
            return redirect('expedientes:mesa_dashboard')
    else:
        form = ExpedienteMesaForm()

    return render(request, 'expedientes/crear_expediente_mesa.html', {
        'form': form,
        'funcionario': funcionario
    })

@login_required
def confirmar_expediente_mesa(request, id_expediente):
    funcionario = getattr(request.user, 'funcionario_link', None)
    if not funcionario or not (funcionario.departamento and 'mesa' in funcionario.departamento.nombre.lower()):
        return redirect('portal:dashboard')
        
    expediente = get_object_or_404(Expediente, id_expediente=id_expediente)
    
    if request.method == 'POST':
        form = ConfirmarExpedienteMesaForm(request.POST)
        if form.is_valid():
            # Confirmar y Numerar
            expediente.confirmado = True
            expediente.estado = 'En trámite'
            expediente.registrado_por = f"{funcionario.apellido}, {funcionario.nombre}"
            
            # Destino del primer pase oficial
            expediente.actual_area = form.cleaned_data.get('destino_area')
            expediente.actual_direccion = form.cleaned_data.get('destino_direccion')
            expediente.actual_departamento = form.cleaned_data.get('destino_departamento')
            expediente.actual_oficina = form.cleaned_data.get('destino_oficina')
            expediente.save() # Aquí se genera el nro_expediente
            
            # Crear Movimiento
            mov = MovimientoExpediente.objects.create(
                expediente=expediente,
                destino_area=expediente.actual_area,
                destino_direccion=expediente.actual_direccion,
                destino_departamento=expediente.actual_departamento,
                destino_oficina=expediente.actual_oficina,
                observacion=form.cleaned_data.get('nota_mesa'),
                usuario_emisor=expediente.registrado_por,
                estado='Confirmado'
            )
            generar_notificaciones_destino(expediente, mov)
            
            messages.success(request, f"Expediente confirmado. Se le ha asignado el número: {expediente.nro_expediente}")
            return redirect('expedientes:mesa_dashboard')
    else:
        # Previsualizar datos de destino sugeridos por el solicitante
        initial_data = {
            'destino_oficina': expediente.oficina_destino_sugerida,
            'destino_departamento': expediente.oficina_destino_sugerida.departamento if expediente.oficina_destino_sugerida else None,
        }
        form = ConfirmarExpedienteMesaForm(initial=initial_data)

    return render(request, 'expedientes/confirmar_expediente_mesa.html', {
        'expediente': expediente,
        'form': form,
        'funcionario': funcionario
    })


