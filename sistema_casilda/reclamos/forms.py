from django import forms
from .models import Reclamo

class ReclamoForm(forms.ModelForm):
    class Meta:
        model = Reclamo
        fields = ['area', 'tipo_reclamo', 'calle', 'numero', 'barrio', 'observacion', 'foto']
        widgets = {
            'area': forms.Select(attrs={'class': 'form-select area-select'}),
            'tipo_reclamo': forms.Select(attrs={'class': 'form-select tipo-select'}),
            'calle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: San Martín'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1234 o s/n'}),
            'barrio': forms.Select(attrs={'class': 'form-select'}),
            'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describa el problema aquí...'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }
