from django import forms
from django.contrib.auth.models import User
from .models import Funcionario

class FuncionarioForm(forms.ModelForm):
    password_nueva = forms.CharField(
        widget=forms.PasswordInput(), 
        required=False, 
        help_text="Opcional. Ingrese una clave para que el empleado use en el login nativo."
    )

    class Meta:
        model = Funcionario
        exclude = ('pass_salt', 'pass_hash', 'user')

    def save(self, commit=True):
        funcionario = super().save(commit=False)
        password_nueva = self.cleaned_data.get('password_nueva')

        # Vínculo e instanciación de usuario para login local
        user, _ = User.objects.get_or_create(username=funcionario.usuario_login)
        user.first_name = funcionario.nombre or ''
        user.last_name = funcionario.apellido or ''
        user.email = funcionario.email or ''
        user.is_active = (funcionario.activo == 'S')
        user.is_staff = True
        
        if password_nueva:
            user.set_password(password_nueva)
            import hashlib
            funcionario.pass_hash = hashlib.sha256(password_nueva.encode()).hexdigest()
        
        user.save()
        funcionario.user = user

        if commit:
            funcionario.save()
        return funcionario
