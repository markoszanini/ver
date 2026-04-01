from django import forms
from .models import Expediente
from organigrama.models import Area, Direccion, Departamento, Oficina

class ExpedienteInternalForm(forms.ModelForm):
    # Campos ocultos para el destino inteligente
    destino_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    destino_type = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Expediente
        fields = ['asunto', 'dirigido_a', 'destino_oficina_sugerido', 'foto', 'observaciones']
        widgets = {
            'asunto': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Describa el motivo del expediente...'}),
            'dirigido_a': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre o Cargo del destinatario'}),
            'destino_oficina_sugerido': forms.HiddenInput(),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

class ExpedienteMesaForm(forms.ModelForm):
    dni_vecino = forms.CharField(required=False, label="DNI Titular", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DNI para buscar vecino...'}))
    
    # Campos ocultos para el destino inteligente
    destino_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    destino_type = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Expediente
        fields = ['asunto', 'dirigido_a', 'destino_oficina_sugerido', 'foto', 'observaciones', 
                  'nombre_titular_manual', 'apellido_titular_manual', 'dni_titular_manual']
        widgets = {
            'asunto': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Motivo del expediente...'}),
            'dirigido_a': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Destinatario final'}),
            'destino_oficina_sugerido': forms.HiddenInput(),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'nombre_titular_manual': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_titular_manual': forms.TextInput(attrs={'class': 'form-control'}),
            'dni_titular_manual': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ConfirmarExpedienteMesaForm(forms.Form):
    # Campos ocultos para el destino inteligente
    destino_id = forms.CharField(widget=forms.HiddenInput(), required=True)
    destino_type = forms.CharField(widget=forms.HiddenInput(), required=True)
    nota_mesa = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Observaciones de Mesa de Entrada...'}), required=False, label="Observaciones")

class PaseExpedienteForm(forms.Form):
    # Campos ocultos para el destino inteligente
    destino_id = forms.CharField(widget=forms.HiddenInput(), required=True)
    destino_type = forms.CharField(widget=forms.HiddenInput(), required=True)
    observacion_pase = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Breve nota para la oficina de destino...'}), required=False, label="Nota de Pase")
