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

        # Si no hay usuario_login, lo generamos automáticamente
        if not funcionario.usuario_login:
            base_username = f"{funcionario.nombre.split()[0]}.{funcionario.apellido.split()[0]}".lower().replace(" ", "")
            
            # 1. Intentar nombre.apellido
            username = base_username
            
            # 2. Si colisiona y hay segundo nombre, intentar nombresegundo.apellido
            if User.objects.filter(username=username).exists() and funcionario.segundo_nombre:
                username = f"{funcionario.nombre.split()[0]}{funcionario.segundo_nombre.split()[0]}.{funcionario.apellido.split()[0]}".lower().replace(" ", "")
            
            # 3. Si sigue colisionando, agregar sufijo numérico
            original_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{original_username}.{counter}"
                counter += 1
            
            funcionario.usuario_login = username

        # Vínculo e instanciación de usuario para login local
        user, created = User.objects.get_or_create(username=funcionario.usuario_login)
        user.first_name = funcionario.nombre or ''
        user.last_name = funcionario.apellido or ''
        user.email = funcionario.email or ''
        user.is_active = (funcionario.activo == 'S')
        user.is_staff = True
        
        # Si no tiene password y es nuevo, usar el DNI como clave inicial
        if created and not password_nueva and funcionario.dni:
            user.set_password(funcionario.dni)
        elif password_nueva:
            user.set_password(password_nueva)
            import hashlib
            funcionario.pass_hash = hashlib.sha256(password_nueva.encode()).hexdigest()
        
        user.save()
        funcionario.user = user

        if commit:
            funcionario.save()
        return funcionario
