
from django.db import models

class RubroEmpleo(models.Model):
    id_rubro = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)
    activo = models.CharField(max_length=1, default='S', choices=[('S','Sí'), ('N','No')])
    def __str__(self): return self.descripcion
    
    class Meta:
        ordering = ['descripcion']

class PuestoEmpleo(models.Model):
    id_puesto = models.AutoField(primary_key=True)
    rubro = models.ForeignKey(RubroEmpleo, on_delete=models.CASCADE, related_name='puestos')
    descripcion = models.CharField(max_length=150)
    activo = models.CharField(max_length=1, default='S', choices=[('S','Sí'), ('N','No')])
    def __str__(self): return f"{self.rubro.descripcion} - {self.descripcion}"
    
    class Meta:
        ordering = ['descripcion']

class Postulante(models.Model):
    SN_CHOICES = [('S', 'Sí'), ('N', 'No')]
    DISPONIBILIDAD_CHOICES = [
        ('2', 'Mañana'),
        ('21', 'Part Time'),
        ('23', 'Fin de Semana'),
        ('1', 'Full Time'),
        ('22', 'Turnos Rotativos'),
        ('3', 'Tarde'),
    ]
    LICENCIA_CHOICES = [
        ('2', 'A'),
        ('21', 'B1'),
        ('3', 'B2'),
        ('4', 'C'),
        ('5', 'D'),
        ('22', 'E'),
        ('6', 'Profesional'),
    ]
    SITUACION_CHOICES = [
        ('1', 'Desocupado'),
        ('2', 'Estudiante'),
        ('3', 'Changas/Eventual'),
        ('4', 'Monotributista'),
        ('21', 'Empleado'),
    ]
    LOCALIDAD_CHOICES = [
        ('1', 'Casilda'),
        ('2', 'Arteaga'),
        ('3', 'Arequito'),
        ('4', 'Berabevú'),
        ('5', 'Chañar Ladeado'),
        ('6', 'Gödeken'),
        ('7', 'Sanford'),
        ('21', 'Bigand'),
        ('22', 'Chabás'),
        ('23', 'Los Molinos'),
        ('24', 'Villada'),
        ('25', 'Fuentes'),
        ('100', 'Rosario'),
        ('101', 'Venado Tuerto'),
        ('102', 'San Lorenzo'),
        ('103', 'Villa Constitución'),
        ('104', 'Firmat'),
        ('105', 'Roldán'),
        ('106', 'Funes'),
        ('107', 'Pujato'),
        ('108', 'Zavalla'),
        ('109', 'Pérez'),
        ('8', 'Otro'),
    ]
    id_postulante = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    apellido = models.CharField(max_length=150)
    fecha_nac = models.DateField(blank=True, null=True)
    sexo = models.CharField(max_length=30, blank=True, null=True)
    domicilio = models.CharField(max_length=200, blank=True, null=True)
    localidad = models.CharField(max_length=100, blank=True, null=True, choices=LOCALIDAD_CHOICES)
    localidad_detalle = models.CharField(max_length=200, blank=True, null=True)
    cp = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    mail = models.EmailField(max_length=150, blank=True, null=True)
    situacion_actual = models.CharField(max_length=50, blank=True, null=True, choices=SITUACION_CHOICES)
    sobre_mi = models.TextField(blank=True, null=True)
    movilidad_propia = models.CharField(max_length=1, default='N', choices=SN_CHOICES)
    medio_movilidad = models.CharField(max_length=50, blank=True, null=True)
    licencia_conducir = models.CharField(max_length=1, default='N', choices=SN_CHOICES)
    licencia_categoria = models.CharField(max_length=50, blank=True, null=True, choices=LICENCIA_CHOICES)
    licencia_vencimiento = models.DateField(blank=True, null=True)
    disponibilidad_viajar = models.CharField(max_length=1, default='N', choices=SN_CHOICES)
    disponibilidad_horaria = models.CharField(max_length=200, blank=True, null=True, choices=DISPONIBILIDAD_CHOICES)
    estado = models.CharField(max_length=30, default='ACTIVO')
    fecha_alta = models.DateTimeField(auto_now_add=True)
    puestos = models.ManyToManyField(PuestoEmpleo, blank=True)
    vecino = models.ForeignKey('portal.Vecino', on_delete=models.SET_NULL, null=True, blank=True, related_name='postulaciones_empleo', verbose_name="Vecino Titular")
    cv = models.FileField(upload_to='empleo/cvs/', blank=True, null=True, verbose_name="Curriculum Vitae (PDF)")

    class Meta:
        verbose_name = "Formulario Postulante"
        verbose_name_plural = "Postulantes"
        ordering = ['apellido', 'nombre']

    def __str__(self): return f"{self.apellido}, {self.nombre}"

class Curso(models.Model):
    id_curso = models.AutoField(primary_key=True)
    postulante = models.ForeignKey(Postulante, on_delete=models.CASCADE, related_name='cursos')
    curso = models.CharField(max_length=200, blank=True, null=True)
    institucion_cursos = models.CharField(max_length=200, blank=True, null=True)
    anio_cursos = models.CharField(max_length=10, blank=True, null=True)
    certificado = models.FileField(upload_to='empleo/certificados/', blank=True, null=True)
    fecha_carga = models.DateTimeField(auto_now_add=True)

class Experiencia(models.Model):
    id_experiencia = models.AutoField(primary_key=True)
    postulante = models.ForeignKey(Postulante, on_delete=models.CASCADE, related_name='experiencias')
    rubro = models.ForeignKey(RubroEmpleo, on_delete=models.SET_NULL, blank=True, null=True)
    puesto = models.ForeignKey(PuestoEmpleo, on_delete=models.SET_NULL, blank=True, null=True)
    empresa = models.CharField(max_length=150)
    fecha_desde = models.DateField(blank=True, null=True)
    fecha_hasta = models.DateField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    referencia = models.CharField(max_length=300, blank=True, null=True)

class Estudio(models.Model):
    id_estudio = models.AutoField(primary_key=True)
    postulante = models.ForeignKey(Postulante, on_delete=models.CASCADE, related_name='estudios')
    nivel = models.CharField(max_length=30, blank=True, null=True)
    carrera = models.CharField(max_length=200, blank=True, null=True)
    institucion = models.CharField(max_length=200, blank=True, null=True)
    anio = models.CharField(max_length=10, blank=True, null=True)
    estado_estudio = models.CharField(max_length=20, blank=True, null=True)

class Idioma(models.Model):
    NIVEL_CHOICES = [('BASICO','Básico'), ('INTERMEDIO','Intermedio'), ('AVANZADO','Avanzado'), ('NATIVO','Nativo')]
    SN_CHOICES = [('S', 'Sí'), ('N', 'No')]
    IDIOMA_CHOICES = [
        ('1', 'Español'),
        ('2', 'Inglés'),
        ('3', 'Portugués'),
        ('4', 'Francés'),
        ('5', 'Alemán'),
        ('6', 'Chino Mandarín'),
        ('7', 'Lengua de Señas Argentina'),
        ('21', 'Italiano'),
        ('8', 'Otro'),
    ]
    id_idioma = models.AutoField(primary_key=True)
    postulante = models.ForeignKey(Postulante, on_delete=models.CASCADE, related_name='idiomas')
    idioma = models.CharField(max_length=100, choices=IDIOMA_CHOICES)
    lee = models.CharField(max_length=1, default='N', choices=SN_CHOICES)
    habla = models.CharField(max_length=1, default='N', choices=SN_CHOICES)
    escribe = models.CharField(max_length=1, default='N', choices=SN_CHOICES)
    nivel_idiomas = models.CharField(max_length=20, blank=True, null=True, choices=NIVEL_CHOICES)

class Postulacion(models.Model):
    id_postulacion = models.AutoField(primary_key=True)
    postulante = models.ForeignKey(Postulante, on_delete=models.CASCADE, related_name='postulaciones')
    puesto = models.ForeignKey(PuestoEmpleo, on_delete=models.SET_NULL, blank=True, null=True)
    rubro = models.ForeignKey(RubroEmpleo, on_delete=models.SET_NULL, blank=True, null=True)
    orden = models.PositiveIntegerField(blank=True, null=True)
