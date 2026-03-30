from django import forms
from django.forms import inlineformset_factory
from .models import OrdenCompra, DetalleOrdenCompra

class OrdenCompraPortalForm(forms.ModelForm):
    class Meta:
        model = OrdenCompra
        fields = ['destino', 'origen_fondos', 'observaciones', 'archivo_orden']
        widgets = {
            'destino': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Destino del pedido...'}),
            'origen_fondos': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Partida o fondos...'}),
            'observaciones': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Notas adicionales...'}),
            'archivo_orden': forms.FileInput(attrs={'class': 'form-control'}),
        }

class DetalleOrdenCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleOrdenCompra
        fields = ['cantidad_pedida', 'descripcion']
        widgets = {
            'cantidad_pedida': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Producto / Servicio...'}),
        }

DetalleOrdenCompraFormSet = inlineformset_factory(
    OrdenCompra, DetalleOrdenCompra,
    form=DetalleOrdenCompraForm,
    extra=1,
    can_delete=True
)
