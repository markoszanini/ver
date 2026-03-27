from django.db import models
from django.contrib.auth.models import User
from organigrama.models import Funcionario

class CategoriaSalarial(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre de Categoría")
    sueldo_basico = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Sueldo Básico")

    class Meta:
        verbose_name = "Categoría Salarial"
        verbose_name_plural = "Categorías Salariales"

    def __str__(self):
        return f"{self.nombre} (${self.sueldo_basico})"

class InformacionSalarial(models.Model):
    funcionario = models.OneToOneField(Funcionario, on_delete=models.CASCADE, related_name='info_salarial', verbose_name="Empleado")
    categoria = models.ForeignKey(CategoriaSalarial, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoría")
    sueldo_basico_personalizado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Si se deja vacío, se tomará el de la categoría.")
    
    class AdicionalTitulo(models.TextChoices):
        NINGUNO = '0', 'Ninguno (0%)'
        SECUNDARIO = '10', 'Secundario (10%)'
        TERCIARIO_3 = '15', 'Terciario 3 años (15%)'
        UNI_4 = '20', 'Univ. 4 años (20%)'
        UNI_5 = '25', 'Univ. 5+ años o Posgrado (25%)'
        TEC_PRE_UNI = '17.5', 'Técnico o Pre-univ. (17.5%)'

    adicional_titulo_tipo = models.CharField(max_length=10, choices=AdicionalTitulo.choices, default=AdicionalTitulo.NINGUNO, verbose_name="Adicional por Título")
    
    class SuplementoTipo(models.TextChoices):
        NINGUNO = '0', 'Ninguno (0%)'
        RIESGO = '20', 'Riesgo y Peligrosidad (20%)'
        DEDICACION = '40', 'Dedicación Exclusiva (40%)'
        TAREAS_ESPECIALES = '15', 'Tareas Especiales/Asistenciales (15%)'
        RESPONSABILIDAD = '25', 'Responsabilidad Jerárquica (25%)'
        MAYOR_JORNADA = '50', 'Mayor Jornada Laboral (50%)'

    suplemento_tipo = models.CharField(max_length=10, choices=SuplementoTipo.choices, default=SuplementoTipo.NINGUNO, verbose_name="Suplemento Especial")

    adicional_antiguedad_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=2.00, verbose_name="% Antigüedad por Año")
    suplemento_presentismo = models.BooleanField(default=True, verbose_name="Cobra Presentismo")
    otros_adicionales_fijos = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Otros Adicionales (Suma Fija)")

    class Meta:
        verbose_name = "Información Salarial"
        verbose_name_plural = "Información Salarial de Empleados"

    def __str__(self):
        return f"Config. Salarial - {self.funcionario.usuario_login}"
    
    @property
    def sueldo_basico_aplicable(self):
        if self.sueldo_basico_personalizado:
            return self.sueldo_basico_personalizado
        return self.categoria.sueldo_basico if self.categoria else 0

class LiquidacionMensual(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='liquidaciones', verbose_name="Empleado")
    mes = models.IntegerField(choices=[(i, str(i)) for i in range(1, 13)], verbose_name="Mes")
    anio = models.IntegerField(default=2026, verbose_name="Año")
    
    sueldo_bruto = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Sueldo Bruto")
    total_descuentos = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total Descuentos")
    sueldo_neto = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Sueldo Neto")
    
    detalles_json = models.JSONField(null=True, blank=True, help_text="Desglose detallado de la liquidación.")
    fecha_proceso = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Liquidación Mensual"
        verbose_name_plural = "Historial de Liquidaciones"
        unique_together = ('funcionario', 'mes', 'anio')

    def __str__(self):
        return f"Liq. {self.mes}/{self.anio} - {self.funcionario.usuario_login}"

class Familiar(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='familiares', verbose_name="Empleado")
    nombre_completo = models.CharField(max_length=200, verbose_name="Nombre Completo")
    
    class Parentesco(models.TextChoices):
        CONYUGE = 'CONYUGE', 'Cónyuge'
        HIJO = 'HIJO', 'Hijo/a'
        PADRE = 'PADRE', 'Padre'
        MADRE = 'MADRE', 'Madre'
        OTRO = 'OTRO', 'Otro'

    parentesco = models.CharField(max_length=20, choices=Parentesco.choices, verbose_name="Parentesco")
    dni = models.CharField(max_length=20, null=True, blank=True, verbose_name="DNI")
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de Nacimiento")
    discapacidad = models.BooleanField(default=False, verbose_name="Posee Discapacidad")
    escolaridad = models.BooleanField(default=False, verbose_name="En Escolaridad")

    class Meta:
        verbose_name = "Familiar"
        verbose_name_plural = "Datos Familiares"

class FormacionAcademica(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='formacion', verbose_name="Empleado")
    
    class Nivel(models.TextChoices):
        PRIMARIO = 'PRIMARIO', 'Primario'
        SECUNDARIO = 'SECUNDARIO', 'Secundario'
        TERCIARIO = 'TERCIARIO', 'Terciario'
        UNIVERSITARIO = 'UNIVERSITARIO', 'Universitario'
        POSGRADO = 'POSGRADO', 'Posgrado'
        CURSO = 'CURSO', 'Curso/Certificación'

    nivel = models.CharField(max_length=20, choices=Nivel.choices, verbose_name="Nivel Educativo")
    titulo = models.CharField(max_length=200, verbose_name="Título / Nombre del Curso")
    institucion = models.CharField(max_length=200, verbose_name="Institución")
    
    class Estado(models.TextChoices):
        COMPLETO = 'COMPLETO', 'Completo'
        EN_CURSO = 'EN_CURSO', 'En Curso'
        INCOMPLETO = 'INCOMPLETO', 'Incompleto'

    estado = models.CharField(max_length=20, choices=Estado.choices, verbose_name="Estado")
    fecha_fin = models.DateField(null=True, blank=True, verbose_name="Fecha de Finalización")

    class Meta:
        verbose_name = "Formación Académica"
        verbose_name_plural = "Estudios y Cursos"

class ExperienciaLaboral(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='experiencia', verbose_name="Empleado")
    empresa = models.CharField(max_length=200, verbose_name="Empresa / Organismo")
    cargo = models.CharField(max_length=200, verbose_name="Cargo / Función")
    fecha_desde = models.DateField(verbose_name="Desde")
    fecha_hasta = models.DateField(null=True, blank=True, verbose_name="Hasta")
    tareas = models.TextField(null=True, blank=True, verbose_name="Tareas Realizadas")
    es_trabajo_actual = models.BooleanField(default=False, verbose_name="Es Trabajo Actual")

    class Meta:
        verbose_name = "Experiencia Laboral"
        verbose_name_plural = "Historia Laboral Previa"

class ReciboSueldo(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='recibos', verbose_name="Empleado")
    archivo = models.FileField(upload_to='recibos/%Y/%m/', verbose_name="Archivo PDF")
    mes = models.IntegerField(choices=[(i, str(i)) for i in range(1, 13)], verbose_name="Mes")
    anio = models.IntegerField(default=2026, verbose_name="Año")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Recibo de Sueldo"
        verbose_name_plural = "Recibos de Sueldo"
        ordering = ['-anio', '-mes']

    def __str__(self):
        return f"Recibo {self.mes}/{self.anio} - {self.funcionario.usuario_login}"

class Vacaciones(models.Model):
    funcionario = models.OneToOneField(Funcionario, on_delete=models.CASCADE, related_name='vacaciones', verbose_name="Empleado")
    anio_correspondiente = models.IntegerField(default=2025, verbose_name="Año Correspondiente")
    dias_totales = models.IntegerField(default=14, verbose_name="Días Totales")
    dias_tomados = models.IntegerField(default=0, verbose_name="Días Tomados")
    
    @property
    def dias_disponibles(self):
        return self.dias_totales - self.dias_tomados

    class Meta:
        verbose_name = "Vacaciones"
        verbose_name_plural = "Control de Vacaciones"

    def __str__(self):
        return f"Vacaciones {self.funcionario.usuario_login}"

class NovedadRRHH(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    mensaje = models.TextField(verbose_name="Mensaje")
    fecha = models.DateTimeField(auto_now_add=True)
    es_general = models.BooleanField(default=True, verbose_name="¿Es para todos?")
    funcionario_destino = models.ForeignKey(Funcionario, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Empleado Específico")

    class Meta:
        verbose_name = "Novedad de RRHH"
        verbose_name_plural = "Novedades de RRHH"
        ordering = ['-fecha']

    def __str__(self):
        return self.titulo

class Empleado(Funcionario):
    class Meta:
        proxy = True
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados (Legajos)"
