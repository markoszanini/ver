from django import forms
from .models import Expediente
from organigrama.models import Area, Direccion, Departamento, Oficina

class ExpedienteInternalForm(forms.ModelForm):
    class Meta:
        model = Expediente
        fields = ['asunto', 'dirigido_a', 'oficina_destino_sugerida', 'foto', 'observaciones']
        widgets = {
            'asunto': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Describa el motivo del expediente...'}),
            'dirigido_a': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre o Cargo del destinatario'}),
            'oficina_destino_sugerida': forms.Select(attrs={'class': 'form-control select2'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

class ExpedienteMesaForm(forms.ModelForm):
    dni_vecino = forms.CharField(required=False, label="DNI Titular", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DNI para buscar vecino...'}))
    
    class Meta:
        model = Expediente
        fields = ['asunto', 'dirigido_a', 'oficina_destino_sugerida', 'foto', 'observaciones', 
                  'nombre_titular_manual', 'apellido_titular_manual', 'dni_titular_manual']
        widgets = {
            'asunto': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Motivo del expediente...'}),
            'dirigido_a': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Destinatario final'}),
            'oficina_destino_sugerida': forms.Select(attrs={'class': 'form-control select2'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'nombre_titular_manual': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_titular_manual': forms.TextInput(attrs={'class': 'form-control'}),
            'dni_titular_manual': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ConfirmarExpedienteMesaForm(forms.Form):
    destino_area = forms.ModelChoiceField(queryset=Area.objects.all(), required=False, label="Área de Destino", widget=forms.Select(attrs={'class': 'form-select select2'}))
    destino_direccion = forms.ModelChoiceField(queryset=Direccion.objects.all(), required=False, label="Dirección", widget=forms.Select(attrs={'class': 'form-select select2'}))
    destino_departamento = forms.ModelChoiceField(queryset=Departamento.objects.all(), required=False, label="Departamento", widget=forms.Select(attrs={'class': 'form-select select2'}))
    destino_oficina = forms.ModelChoiceField(queryset=Oficina.objects.all(), required=False, label="Oficina", widget=forms.Select(attrs={'class': 'form-select select2'}))
    nota_mesa = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Observaciones de Mesa de Entrada...'}), required=False, label="Observaciones")

class PaseExpedienteForm(forms.Form):
    destino_area = forms.ModelChoiceField(queryset=Area.objects.all(), required=False, label="Área de Destino", widget=forms.Select(attrs={'class': 'form-select select2'}))
    destino_direccion = forms.ModelChoiceField(queryset=Direccion.objects.all(), required=False, label="Dirección", widget=forms.Select(attrs={'class': 'form-select select2'}))
    destino_departamento = forms.ModelChoiceField(queryset=Departamento.objects.all(), required=False, label="Departamento", widget=forms.Select(attrs={'class': 'form-select select2'}))
    destino_oficina = forms.ModelChoiceField(queryset=Oficina.objects.all(), required=False, label="Oficina", widget=forms.Select(attrs={'class': 'form-select select2'}))
    observacion_pase = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Breve nota para la oficina de destino...'}), required=False, label="Nota de Pase")
