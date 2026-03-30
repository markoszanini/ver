from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Expediente
from .forms import ExpedienteInternalForm
from organigrama.models import Funcionario, Departamento

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
        
    # Ve los expedientes donde él es el solicitante_interno O creador_por
    from django.db.models import Q
    expedientes = Expediente.objects.filter(
        Q(creado_por=request.user) | Q(solicitante_interno=funcionario)
    ).order_by('-fecha_ingreso').distinct()
    
    return render(request, 'expedientes/mis_expedientes_internos.html', {'expedientes': expedientes})

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
            
            # Obtener nombre de origen para el mensaje
            origen_stmt = "Iniciado correctamente."
            if funcionario.oficina:
                origen_stmt = f"Expediente interno de {funcionario.oficina.nombre} iniciado correctamente."
            elif funcionario.departamento:
                origen_stmt = f"Expediente interno de {funcionario.departamento.nombre} iniciado correctamente."
                
            messages.success(request, origen_stmt)
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
