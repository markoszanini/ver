from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import (RegistroVecinoForm, PostulanteForm, FerianteForm, 
                    PostulacionFormSet, ExperienciaFormSet, EstudioFormSet, CursoFormSet, IdiomaFormSet)
from empleo.models import Postulante
from ferias.models import Feriante

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
    try:
        vecino = request.user.vecino_profile
        from expedientes.models import Expediente
        expedientes = Expediente.objects.filter(vecino_titular=vecino)
    except Exception:
        expedientes = []
    return render(request, 'portal/dashboard.html', {'expedientes': expedientes})

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
