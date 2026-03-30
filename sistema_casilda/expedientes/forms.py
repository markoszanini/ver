from django import forms
from .models import Expediente

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
