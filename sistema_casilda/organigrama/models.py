from django.db import models
from django.contrib.auth.models import User

class Area(models.Model):
    id_area = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)

    class Meta:
        db_table = 'REGIO_AREAS'
        verbose_name = 'Área'
        verbose_name_plural = 'Áreas'

    def __str__(self):
        return self.nombre

class Direccion(models.Model):
    id_direccion = models.AutoField(primary_key=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, db_column='ID_AREA')
    nombre = models.CharField(max_length=200)

    class Meta:
        db_table = 'REGIO_DIRECCIONES'
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'

    def __str__(self):
        return f"{self.nombre} ({self.area.nombre})"

class Departamento(models.Model):
    id_departamento = models.AutoField(primary_key=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, db_column='ID_AREA', null=True, blank=True)
    direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE, db_column='ID_DIRECCION', null=True, blank=True)
    nombre = models.CharField(max_length=200)

    class Meta:
        db_table = 'REGIO_DEPARTAMENTOS'
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'

    def __str__(self):
        return self.nombre

class Division(models.Model):
    id_division = models.AutoField(primary_key=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, db_column='ID_DEPARTAMENTO')
    nombre = models.CharField(max_length=200)

    class Meta:
        db_table = 'REGIO_DIVISIONES'
        verbose_name = 'División'
        verbose_name_plural = 'Divisiones'

    def __str__(self):
        return self.nombre

class Subdivision(models.Model):
    id_subdivision = models.AutoField(primary_key=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, db_column='ID_DIVISION', null=True, blank=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, db_column='ID_DEPARTAMENTO', null=True, blank=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, db_column='ID_AREA', null=True, blank=True)
    nombre = models.CharField(max_length=200)

    class Meta:
        db_table = 'REGIO_SUBDIVISIONES'
        verbose_name = 'Subdivisión'
        verbose_name_plural = 'Subdivisiones'

    def __str__(self):
        return self.nombre

class Seccion(models.Model):
    id_seccion = models.AutoField(primary_key=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, db_column='ID_DIVISION', null=True, blank=True)
    subdivision = models.ForeignKey(Subdivision, on_delete=models.CASCADE, db_column='ID_SUBDIVISION', null=True, blank=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, db_column='ID_DEPARTAMENTO', null=True, blank=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, db_column='ID_AREA', null=True, blank=True)
    nombre = models.CharField(max_length=200)

    class Meta:
        db_table = 'REGIO_SECCIONES'
        verbose_name = 'Sección'
        verbose_name_plural = 'Secciones'

    def __str__(self):
        return self.nombre

class Oficina(models.Model):
    id_oficina = models.AutoField(primary_key=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, db_column='ID_AREA', null=True, blank=True)
    direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE, db_column='ID_DIRECCION', null=True, blank=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, db_column='ID_DEPARTAMENTO', null=True, blank=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, db_column='ID_DIVISION', null=True, blank=True)
    subdivision = models.ForeignKey(Subdivision, on_delete=models.CASCADE, db_column='ID_SUBDIVISION', null=True, blank=True)
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE, db_column='ID_SECCION', null=True, blank=True)
    nombre = models.CharField(max_length=200)

    class Meta:
        db_table = 'REGIO_OFICINAS'
        verbose_name = 'Oficina'
        verbose_name_plural = 'Oficinas'

    def __str__(self):
        return self.nombre

class RangoEmpleado(models.TextChoices):
    JEFE = 'JEFE', 'Jefe'
    SECRETARIO = 'SECRETARIO', 'Secretario'
    ADMINISTRATIVO = 'ADMINISTRATIVO', 'Administrativo'
    INSPECTOR = 'INSPECTOR', 'Inspector'
    OPERARIO = 'OPERARIO', 'Operario'

class Funcionario(models.Model):
    id_funcionario = models.AutoField(primary_key=True, db_column='ID_FUNCIONARIO')
    nro_legajo = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="Número de Legajo")
    id_empleado_externo = models.IntegerField(unique=True, null=True, blank=True, db_column='ID_EMPLEADO_EXTERNO')
    usuario_login = models.CharField(max_length=100, unique=True, db_column='USUARIO_LOGIN')
    pass_salt = models.CharField(max_length=64, null=True, blank=True, db_column='PASS_SALT')
    pass_hash = models.CharField(max_length=64, null=True, blank=True, db_column='PASS_HASH')
    activo = models.CharField(max_length=1, default='S', db_column='ACTIVO')
    fecha_alta = models.DateTimeField(auto_now_add=True, db_column='FECHA_ALTA')
    nombre = models.CharField(max_length=100, null=True, blank=True, db_column='NOMBRE')
    apellido = models.CharField(max_length=100, null=True, blank=True, db_column='APELLIDO')
    email = models.EmailField(max_length=200, null=True, blank=True, db_column='EMAIL')

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='funcionario_link', null=True, blank=True)
    
    segundo_nombre = models.CharField(max_length=100, null=True, blank=True, verbose_name="Segundo Nombre")
    dni = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="DNI")
    cuil = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="CUIL")
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de Nacimiento")
    
    class Genero(models.TextChoices):
        MASCULINO = 'M', 'Masculino'
        FEMENINO = 'F', 'Femenino'
        OTRO = 'O', 'Otro'
    
    genero = models.CharField(max_length=1, choices=Genero.choices, null=True, blank=True, verbose_name="Género")
    
    class EstadoCivil(models.TextChoices):
        SOLTERO = 'SOLTERO', 'Soltero/a'
        CASADO = 'CASADO', 'Casado/a'
        DIVORCIADO = 'DIVORCIADO', 'Divorciado/a'
        VIUDO = 'VIUDO', 'Viudo/a'
        CONVIVIENTE = 'CONVIVIENTE', 'Conviviente'

    estado_civil = models.CharField(max_length=20, choices=EstadoCivil.choices, default=EstadoCivil.SOLTERO, verbose_name="Estado Civil")
    
    calle = models.CharField(max_length=200, null=True, blank=True, verbose_name="Calle")
    altura = models.CharField(max_length=10, null=True, blank=True, verbose_name="Altura")
    telefono = models.CharField(max_length=50, null=True, blank=True, verbose_name="Teléfono Fijo")
    celular = models.CharField(max_length=50, null=True, blank=True, verbose_name="Celular")

    rango = models.CharField(max_length=50, choices=RangoEmpleado.choices, default=RangoEmpleado.ADMINISTRATIVO)
    
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True, db_column='ID_AREA')
    direccion = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True, blank=True, db_column='ID_DIRECCION')
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True, db_column='ID_DEPARTAMENTO')
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True, db_column='ID_DIVISION')
    subdivision = models.ForeignKey(Subdivision, on_delete=models.SET_NULL, null=True, blank=True, db_column='ID_SUBDIVISION')
    seccion = models.ForeignKey(Seccion, on_delete=models.SET_NULL, null=True, blank=True, db_column='ID_SECCION')
    oficina = models.ForeignKey(Oficina, on_delete=models.SET_NULL, null=True, blank=True, db_column='ID_OFICINA')

    class Meta:
        db_table = 'REGIO_FUNCIONARIOS'
        verbose_name = 'Funcionario / Empleado'
        verbose_name_plural = 'Funcionarios'

    def __str__(self):
        return f"{self.apellido or ''}, {self.nombre or ''} ({self.usuario_login})"
