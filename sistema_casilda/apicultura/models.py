from django.db import models

class Apicultor(models.Model):
    id_apicultor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nombre")
    dni = models.CharField(max_length=20, blank=True, null=True, verbose_name="DNI")
    telefono = models.CharField(max_length=30, blank=True, null=True, verbose_name="Teléfono")
    email = models.EmailField(max_length=200, blank=True, null=True, verbose_name="Email")
    localidad = models.CharField(max_length=100, blank=True, null=True, verbose_name="Localidad")
    domicilio = models.CharField(max_length=200, blank=True, null=True, verbose_name="Domicilio")
    cuit_cuil = models.CharField(max_length=20, blank=True, null=True, verbose_name="CUIT/CUIL")
    estado = models.CharField(max_length=15, default='Activo', verbose_name="Estado")
    observaciones = models.TextField(max_length=4000, blank=True, null=True, verbose_name="Observaciones")
    fecha_alta = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Alta")

    class Meta:
        verbose_name = "Apicultor"
        verbose_name_plural = "Apicultores"

    def __str__(self):
        return f"{self.nombre} ({self.cuit_cuil})"

class Extraccion(models.Model):
    FORMA_PAGO_CHOICES = [
        ('ESPECIE', 'Especie'),
        ('DINERO', 'Dinero'),
    ]

    id_extraccion = models.AutoField(primary_key=True)
    apicultor = models.ForeignKey(Apicultor, on_delete=models.CASCADE, related_name='extracciones')
    fecha_extraccion = models.DateField(verbose_name="Fecha de Extracción")
    temporada = models.CharField(max_length=20, blank=True, null=True, verbose_name="Temporada")
    tipo_miel = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tipo de Miel")
    total_kg = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total (Kg)")
    precio_por_kg = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Precio por Kg")
    forma_pago = models.CharField(max_length=10, choices=FORMA_PAGO_CHOICES, verbose_name="Forma de Pago")
    observaciones = models.CharField(max_length=500, blank=True, null=True, verbose_name="Observaciones")
    fecha_carga = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Carga")
    id_operador = models.CharField(max_length=50, blank=True, null=True, verbose_name="Operador")

    class Meta:
        verbose_name = "Extracción"
        verbose_name_plural = "Extracciones"
        ordering = ['-fecha_extraccion']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        v_total_kg = float(self.total_kg or 0)
        v_forma_pago = str(self.forma_pago).upper()
        v_precio_kg = float(self.precio_por_kg or 0) if v_forma_pago == 'DINERO' else 0.0
            
        v_porc_total = 10.0
        v_prop_serv_ext = 0.20
        v_prop_serv_mant = 0.50
        v_prop_muni = 0.30

        v_total_dinero = v_total_kg * v_precio_kg
        v_pago_10_dinero = v_total_dinero * (v_porc_total / 100)
        v_kg_10 = v_total_kg * (v_porc_total / 100)

        # Remove existing liquidaciones (same as APEX: DELETE FROM liquidacion...)
        self.liquidaciones.all().delete()

        # TOTAL (10%)
        LiquidacionExtraccion.objects.create(
            extraccion=self, tipo_concepto='TOTAL', porcentaje_total=v_porc_total,
            kg_9_porciento=v_kg_10 if v_forma_pago == 'ESPECIE' else None,
            importe_9_porciento=v_pago_10_dinero if v_forma_pago == 'DINERO' else None,
            forma_pago=v_forma_pago
        )
        
        # SERV_EXT (2%)
        LiquidacionExtraccion.objects.create(
            extraccion=self, tipo_concepto='SERV_EXT', porcentaje_total=v_porc_total, sub_porcentaje=2,
            kg_9_porciento=v_kg_10 * v_prop_serv_ext if v_forma_pago == 'ESPECIE' else None,
            importe_9_porciento=v_pago_10_dinero * v_prop_serv_ext if v_forma_pago == 'DINERO' else None,
            forma_pago=v_forma_pago
        )
        
        # SERV_MANT (5%)
        LiquidacionExtraccion.objects.create(
            extraccion=self, tipo_concepto='SERV_MANT', porcentaje_total=v_porc_total, sub_porcentaje=5,
            kg_9_porciento=v_kg_10 * v_prop_serv_mant if v_forma_pago == 'ESPECIE' else None,
            importe_9_porciento=v_pago_10_dinero * v_prop_serv_mant if v_forma_pago == 'DINERO' else None,
            forma_pago=v_forma_pago
        )
        
        # MUNICIPALIDAD (3%)
        LiquidacionExtraccion.objects.create(
            extraccion=self, tipo_concepto='MUNICIPALIDAD', porcentaje_total=v_porc_total, sub_porcentaje=3,
            kg_9_porciento=v_kg_10 * v_prop_muni if v_forma_pago == 'ESPECIE' else None,
            importe_9_porciento=v_pago_10_dinero * v_prop_muni if v_forma_pago == 'DINERO' else None,
            forma_pago=v_forma_pago
        )

    def __str__(self):
        return f"Extracción {self.id_extraccion} - {self.apicultor.nombre}"

class LiquidacionExtraccion(models.Model):
    id_liquidacion = models.AutoField(primary_key=True)
    extraccion = models.ForeignKey(Extraccion, on_delete=models.CASCADE, related_name='liquidaciones')
    porcentaje_total = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Porcentaje Total")
    kg_9_porciento = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Kg Retenidos (9%)")
    importe_9_porciento = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="Importe Retenido (9%)")
    forma_pago = models.CharField(max_length=10, choices=Extraccion.FORMA_PAGO_CHOICES, verbose_name="Forma de Pago")
    tipo_concepto = models.CharField(max_length=20, blank=True, null=True, verbose_name="Tipo de Concepto")
    sub_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Sub Porcentaje")

    class Meta:
        verbose_name = "Liquidación"
        verbose_name_plural = "Liquidaciones"

    def __str__(self):
        return f"Liq. {self.id_liquidacion} - {self.extraccion.apicultor.nombre}"

class ApicultorInstitucional(models.Model):
    id_institucional = models.AutoField(primary_key=True)
    apicultor = models.OneToOneField(Apicultor, on_delete=models.CASCADE, related_name='datos_institucionales')
    pertenece_asociacion = models.CharField(max_length=1, default='N', choices=[('S', 'Sí'), ('N', 'No')])
    usa_sala_extraccion = models.CharField(max_length=1, default='S', choices=[('S', 'Sí'), ('N', 'No')])
    extraccion_alter = models.CharField(max_length=500, blank=True, null=True, verbose_name="Extracción Alternativa")

class ApicultorProductivo(models.Model):
    id_productivo = models.AutoField(primary_key=True)
    apicultor = models.OneToOneField(Apicultor, on_delete=models.CASCADE, related_name='datos_productivos')
    cantidad_colmenas = models.PositiveIntegerField(blank=True, null=True, verbose_name="Cantidad de Colmenas")
    ubicacion_apiario = models.CharField(max_length=300, blank=True, null=True, verbose_name="Ubicación Apiario")
    nro_renapa = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nro RENAPA")
    nro_rupp = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nro RUPP")

class ApicultorCapacitacion(models.Model):
    id_capacitacion = models.AutoField(primary_key=True)
    apicultor = models.ForeignKey(Apicultor, on_delete=models.CASCADE, related_name='capacitaciones')
    nombre_capacitacion = models.CharField(max_length=200, verbose_name="Nombre de Capacitación")
    anio_cursado = models.PositiveIntegerField(blank=True, null=True, verbose_name="Año de Cursado")
    titulo_imagen = models.ImageField(upload_to='apicultura/capacitaciones/', blank=True, null=True, verbose_name="Imagen del Título")
    fecha_carga = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Carga")
