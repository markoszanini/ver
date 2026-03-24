from django import forms
from django.contrib.auth.models import User
from .models import Vecino
from empleo.models import Postulante, Postulacion, Experiencia, Estudio, Curso, Idioma
from ferias.models import Feriante

class RegistroVecinoForm(forms.ModelForm):
    dni = forms.CharField(max_length=20, label='DNI', required=True)
    first_name = forms.CharField(max_length=100, label='Nombre', required=True)
    last_name = forms.CharField(max_length=100, label='Apellido', required=True)
    email = forms.EmailField(label='Correo Electrónico', required=True)
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirme la contraseña')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Vecino
        fields = ['telefono', 'domicilio', 'localidad']

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if User.objects.filter(username=dni).exists():
            raise forms.ValidationError("Ya existe un usuario con este DNI.")
        return dni

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        vecino = super().save(commit=False)
        dni = self.cleaned_data['dni']
        # Usamos el DNI como username
        user = User.objects.create_user(
            username=dni,
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        vecino.user = user
        vecino.dni = dni
        if commit:
            vecino.save()
        return vecino

class PostulanteForm(forms.ModelForm):
    class Meta:
        model = Postulante
        exclude = ['id_postulante', 'nombre', 'apellido', 'estado', 'fecha_alta', 'puestos', 'vecino']
        widgets = {
            'fecha_nac': forms.DateInput(attrs={'type': 'date'}),
            'licencia_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

class BaseStyledFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            # If an empty form has a default value for 'orden', it triggers validation errors
            if 'orden' in form.fields and not form.instance.pk:
                form.fields['orden'].initial = None
            
            for name, field in form.fields.items():
                if isinstance(field, forms.DateField):
                    field.widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
                elif isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs.update({'class': 'form-check-input'})
                elif isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                    field.widget.attrs.update({'class': 'form-select'})
                else:
                    field.widget.attrs.update({'class': 'form-control'})

PostulacionFormSet = forms.inlineformset_factory(Postulante, Postulacion, fields='__all__', extra=3, can_delete=True, formset=BaseStyledFormSet)
ExperienciaFormSet = forms.inlineformset_factory(Postulante, Experiencia, fields='__all__', extra=3, can_delete=True, formset=BaseStyledFormSet)
EstudioFormSet = forms.inlineformset_factory(Postulante, Estudio, fields='__all__', extra=3, can_delete=True, formset=BaseStyledFormSet)
CursoFormSet = forms.inlineformset_factory(Postulante, Curso, fields='__all__', extra=3, can_delete=True, formset=BaseStyledFormSet)
IdiomaFormSet = forms.inlineformset_factory(Postulante, Idioma, fields='__all__', extra=3, can_delete=True, formset=BaseStyledFormSet)

class FerianteForm(forms.ModelForm):
    class Meta:
        model = Feriante
        exclude = ['id_feriante', 'nombre', 'apellido', 'dni', 'estado', 'fecha_alta', 'vecino_titular', 'rubros', 'capacitaciones']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
