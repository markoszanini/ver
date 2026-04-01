from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import (RegistroVecinoForm, PostulanteForm, FerianteForm, 
                    PostulacionFormSet, ExperienciaFormSet, EstudioFormSet, CursoFormSet, IdiomaFormSet)
from empleo.models import Postulante
from ferias.models import Feriante, Feria, InscripcionFeria

def home(request):
    if request.user.is_authenticated:
        return redirect('portal:dashboard')
    return render(request, 'portal/home.html')

def login_view(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('portal:login')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('portal:dashboard')
        else:
            messages.error(request, "DNI o contraseña incorrectos.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'portal/login.html', {'form': form})

def registro_view(request):
    if request.user.is_authenticated:
        return redirect('portal:dashboard')
        
    if request.method == 'POST':
        form = RegistroVecinoForm(request.POST)
        if form.is_valid():
            vecino = form.save()
            # Auto-login after registration
            login(request, vecino.user)
            messages.success(request, "¡Registro completado exitosamente!")
            return redirect('portal:dashboard')
    else:
        form = RegistroVecinoForm()
        
    return render(request, 'portal/registro.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('portal:home')

@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect('recursos_humanos:portal_empleado')
        
    vecino = getattr(request.user, 'vecino_profile', None)
    expedientes = []
    notificaciones = []
    reclamos_recientes = []
    reclamos_abiertos = 0
    turnos_proximos = 0
    
    if vecino:
        from expedientes.models import Expediente
        from turnos.models import Turno
        from reclamos.models import Reclamo
        from django.utils import timezone
        from .models import Notificacion
        
        expedientes = Expediente.objects.filter(vecino_titular=vecino).order_by('-fecha_ingreso')
        notificaciones = Notificacion.objects.filter(vecino=vecino, leida=False).order_by('-fecha')
        turnos_proximos = Turno.objects.filter(vecino=vecino, fecha__gte=timezone.now().date()).count()
        
        # Reclamos
        reclamos_all = Reclamo.objects.filter(vecino=vecino)
        reclamos_recientes = reclamos_all.order_by('-fecha_creacion')[:5]
        reclamos_abiertos = reclamos_all.exclude(estado__in=['Resuelto', 'Cerrado']).count()
    
    return render(request, 'portal/dashboard.html', {
        'expedientes': expedientes,
        'notificaciones': notificaciones,
        'turnos_proximos': turnos_proximos,
        'reclamos_recientes': reclamos_recientes,
        'reclamos_abiertos': reclamos_abiertos,
    })

@login_required
def postular_empleo(request):
    try:
        vecino = request.user.vecino_profile
    except Exception:
        from portal.models import Vecino
        vecino = Vecino.objects.create(user=request.user, dni=request.user.username)

    postulante = Postulante.objects.filter(vecino=vecino).first()
    
    if request.method == 'POST':
        form = PostulanteForm(request.POST, request.FILES, instance=postulante)
        formset_postulacion = PostulacionFormSet(request.POST, instance=postulante)
        formset_experiencia = ExperienciaFormSet(request.POST, instance=postulante)
        formset_estudio = EstudioFormSet(request.POST, instance=postulante)
        formset_curso = CursoFormSet(request.POST, instance=postulante)
        formset_idioma = IdiomaFormSet(request.POST, instance=postulante)

        if all([form.is_valid(), formset_postulacion.is_valid(), formset_experiencia.is_valid(), 
                formset_estudio.is_valid(), formset_curso.is_valid(), formset_idioma.is_valid()]):
            p = form.save(commit=False)
            p.vecino = vecino
            p.nombre = request.user.first_name
            p.apellido = request.user.last_name
            p.save()
            
            for fs in [formset_postulacion, formset_experiencia, formset_estudio, formset_curso, formset_idioma]:
                fs.instance = p
                fs.save()

            messages.success(request, "¡CV actualizado y postulado con éxito!")
            return redirect('portal:dashboard')
        else:
            messages.error(request, "Hubo errores en el formulario, por favor revise sus datos.")
    else:
        form = PostulanteForm(instance=postulante)
        formset_postulacion = PostulacionFormSet(instance=postulante)
        formset_experiencia = ExperienciaFormSet(instance=postulante)
        formset_estudio = EstudioFormSet(instance=postulante)
        formset_curso = CursoFormSet(instance=postulante)
        formset_idioma = IdiomaFormSet(instance=postulante)

    context = {
        'form': form,
        'formset_postulacion': formset_postulacion,
        'formset_experiencia': formset_experiencia,
        'formset_estudio': formset_estudio,
        'formset_curso': formset_curso,
        'formset_idioma': formset_idioma,
        'is_update': postulante is not None
    }
    return render(request, 'portal/postular_empleo.html', context)

@login_required
def registro_feriante(request):
    try:
        vecino = request.user.vecino_profile
    except Exception:
        from portal.models import Vecino
        vecino = Vecino.objects.create(user=request.user, dni=request.user.username)

    feriante = Feriante.objects.filter(vecino_titular=vecino).first()
    
    if request.method == 'POST':
        form = FerianteForm(request.POST, request.FILES, instance=feriante)
        if form.is_valid():
            f = form.save(commit=False)
            f.vecino_titular = vecino
            f.dni = request.user.username
            f.nombre = request.user.first_name
            f.apellido = request.user.last_name
            f.save()
            messages.success(request, "¡Tus datos de feriante se guardaron con éxito!")
            return redirect('portal:dashboard')
    else:
        form = FerianteForm(instance=feriante)
    return render(request, 'portal/registro_feriante.html', {'form': form, 'is_update': feriante is not None})

@login_required
def mis_ferias(request):
    vecino = getattr(request.user, 'vecino_profile', None)
    if not vecino:
        messages.error(request, "Debe completar su perfil de vecino primero.")
        return redirect('portal:dashboard')
    
    # Marcar notificaciones como leídas
    from .models import Notificacion
    Notificacion.objects.filter(vecino=vecino, leida=False).update(leida=True)
    
    feriante = Feriante.objects.filter(vecino_titular=vecino).first()
    
    # Ferias disponibles (programadas y a futuro)
    ferias_disponibles = Feria.objects.filter(estado='PROGRAMADA').exclude(inscripciones__feriante=feriante)
    
    # Mis inscripciones
    mis_inscripciones = InscripcionFeria.objects.filter(feriante=feriante).select_related('feria')
    
    return render(request, 'portal/mis_ferias.html', {
        'ferias_disponibles': ferias_disponibles,
        'mis_inscripciones': mis_inscripciones,
        'es_feriante': feriante is not None
    })

@login_required
def inscribirse_feria(request, feria_id):
    if request.method == 'POST':
        vecino = getattr(request.user, 'vecino_profile', None)
        feriante = Feriante.objects.filter(vecino_titular=vecino).first()
        
        if not feriante:
            messages.error(request, "Debe estar registrado como feriante para inscribirse.")
            return redirect('portal:registro_feriante')
            
        feria = Feria.objects.get(id_feria=feria_id)
        InscripcionFeria.objects.get_or_create(feria=feria, feriante=feriante)
        
        messages.success(request, f"Te has inscripto correctamente a {feria.nombre}. Sujeto a validación.")
        
    return redirect('portal:mis_ferias')

@login_required
def omic_view(request):
    return render(request, 'portal/omic.html')
