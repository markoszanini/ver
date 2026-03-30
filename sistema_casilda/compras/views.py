from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import OrdenCompra, DetalleOrdenCompra
from .forms import OrdenCompraPortalForm, DetalleOrdenCompraFormSet
from organigrama.models import Funcionario

@login_required
def iniciar_oc_portal(request):
    try:
        funcionario = getattr(request.user, 'funcionario_link', None)
        if not funcionario:
            messages.error(request, "Solo personal municipal puede emitir órdenes de compra.")
            return redirect('portal:dashboard')

        if request.method == 'POST':
            form = OrdenCompraPortalForm(request.POST, request.FILES)
            formset = DetalleOrdenCompraFormSet(request.POST, request.FILES, prefix='items')
            
            if form.is_valid() and formset.is_valid():
                oc = form.save(commit=False)
                oc.registrado_por = request.user.get_full_name() or request.user.username
                
                # Acceso ultra-seguro a datos de organigrama
                seccion = "S/D"
                if funcionario.oficina:
                    seccion = funcionario.oficina.nombre
                elif funcionario.departamento:
                    seccion = funcionario.departamento.nombre
                elif funcionario.area:
                    seccion = funcionario.area.nombre
                
                oc.seccion_solicita = seccion
                oc.estado = 'En curso'
                oc.save()
                
                # Guardar los items vinculados a la OC
                instances = formset.save(commit=False)
                for i, instance in enumerate(instances):
                    instance.orden_compra = oc
                    instance.item = i + 1
                    instance.save()
                
                messages.success(request, f"Orden de Compra #{oc.id_oc} generada correctamente.")
                return redirect('compras:mis_ordenes_portal')
            else:
                messages.error(request, "Por favor revise los datos ingresados.")
        else:
            form = OrdenCompraPortalForm()
            formset = DetalleOrdenCompraFormSet(prefix='items')

        return render(request, 'compras/iniciar_oc.html', {
            'form': form,
            'formset': formset,
            'funcionario': funcionario
        })
    except Exception as e:
        messages.error(request, f"Error técnico: {str(e)}")
        return redirect('portal:dashboard')

@login_required
def mis_ordenes_portal(request):
    # Asumimos que registrado_por guarda el full name o username
    name = request.user.get_full_name() or request.user.username
    ordenes = OrdenCompra.objects.filter(registrado_por=name).order_by('-fecha_solicitud')
    
    return render(request, 'compras/mis_ordenes.html', {
        'ordenes': ordenes
    })
