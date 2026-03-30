from django.db import models
from portal.models import Vecino
from organigrama.models import Area, Direccion, Departamento, Division, Subdivision, Seccion, Oficina

class Expediente(models.Model):
    id_expediente = models.AutoField(primary_key=True)
    nro_expediente = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="Número de Expediente")
    fecha_ingreso = models.DateField(verbose_name="Fecha de Ingreso", auto_now_add=True)
    
    # Origen (quién lo inició)
    origen_area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes_creados')
    origen_direccion = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes_creados')
    origen_departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes_creados')
    origen_oficina = models.ForeignKey(Oficina, on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes_creados')
    
    asunto = models.TextField(max_length=2000, blank=True, null=True, verbose_name="Asunto")
    
    # Ubicación Actual (dónde está ahora)
    actual_area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes_actuales')
    actual_direccion = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes_actuales')
    actual_departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes_actuales')
    actual_oficina = models.ForeignKey(Oficina, on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes_actuales')

    fecha_salida = models.DateField(blank=True, null=True, verbose_name="Fecha de Finalización")
    estado = models.CharField(max_length=50, default='En trámite', verbose_name="Estado")
    observaciones = models.TextField(max_length=2000, blank=True, null=True, verbose_name="Observaciones")
    registrado_por = models.CharField(max_length=100, blank=True, null=True, verbose_name="Registrado por (Mesa Entrada)")
    foto = models.ImageField(upload_to='expedientes/fotos/', blank=True, null=True, verbose_name="Documento/Foto")
    
    # Opcional: Si el origen fue un vecino
    vecino_titular = models.ForeignKey(Vecino, on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes', verbose_name="Vecino Titular")
    
    # Carga manual para vecinos no registrados
    nombre_titular_manual = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nombre Titular (Manual)")
    apellido_titular_manual = models.CharField(max_length=100, blank=True, null=True, verbose_name="Apellido Titular (Manual)")
    dni_titular_manual = models.CharField(max_length=20, blank=True, null=True, verbose_name="DNI Titular (Manual)")

    # Auditoría y Flujo Interno
    confirmado = models.BooleanField(default=False, verbose_name="Confirmado por Mesa")
    creado_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes_creados_user')
    solicitante_interno = models.ForeignKey('organigrama.Funcionario', on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes_solicitados')

    # Destino para Expedientes Internos
    dirigido_a = models.CharField(max_length=200, blank=True, null=True, verbose_name="Dirigido a (Nombre/Cargo)")
    oficina_destino_sugerida = models.ForeignKey('organigrama.Oficina', on_delete=models.SET_NULL, null=True, blank=True, related_name='expedientes_sugeridos_destino')

    class Meta:
        verbose_name = "Expediente"
        verbose_name_plural = "Expedientes"
        ordering = ['-fecha_ingreso', '-id_expediente']

    def __str__(self):
        return f"{self.nro_expediente or 'S/N'} - {self.asunto[:30] if self.asunto else 'Sin asunto'}..."

    @property
    def origen_display(self):
        if self.vecino_titular:
            return f"Vecino: {self.vecino_titular.user.get_full_name()} (DNI: {self.vecino_titular.dni})"
        if self.dni_titular_manual:
            nombre = f"{self.nombre_titular_manual or ''} {self.apellido_titular_manual or ''}".strip()
            return f"Manual: {nombre} (DNI: {self.dni_titular_manual})"
        if self.origen_oficina:
            return f"Oficina: {self.origen_oficina.nombre}"
        if self.origen_departamento:
            return f"Depto: {self.origen_departamento.nombre}"
        if self.origen_area:
            return f"Área: {self.origen_area.nombre}"
        return "Mesa de Entradas"

    @property
    def ubicacion_display(self):
        if self.actual_oficina:
            return f"Ofi: {self.actual_oficina.nombre}"
        if self.actual_departamento:
            return f"Depto: {self.actual_departamento.nombre}"
        if self.actual_direccion:
            return f"Dir: {self.actual_direccion.nombre}"
        if self.actual_area:
            return f"Área: {self.actual_area.nombre}"
        return "Pendiente de Asignación"

    def save(self, *args, **kwargs):
        # Solo asignar número si está confirmado y aún no tiene uno
        if self.confirmado and not self.nro_expediente:
            import datetime
            anio_actual = datetime.date.today().year
            
            # Buscamos todos los expedientes del año actual para encontrar el máximo
            expedientes_anio = Expediente.objects.filter(nro_expediente__endswith=f"/{anio_actual}")
            
            numeros = []
            for exp in expedientes_anio:
                try:
                    parte_num = exp.nro_expediente.split('/')[0]
                    numeros.append(int(parte_num))
                except (ValueError, IndexError):
                    continue
            
            proximo_numero = max(numeros) + 1 if numeros else 1
            self.nro_expediente = f"{proximo_numero:04d}/{anio_actual}"
            
        # Intentar vinculación automática por DNI si se cargó manual y no hay vínculo
        if not self.vecino_titular and self.dni_titular_manual:
            from portal.models import Vecino
            vecino = Vecino.objects.filter(dni=self.dni_titular_manual).first()
            if vecino:
                self.vecino_titular = vecino
            
        super().save(*args, **kwargs)

class MovimientoExpediente(models.Model):
    id_movimiento = models.AutoField(primary_key=True)
    expediente = models.ForeignKey(Expediente, on_delete=models.CASCADE, related_name='movimientos')
    fecha_pase = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del Pase")
    
    # Destino del Pase
    destino_area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)
    destino_direccion = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True, blank=True)
    destino_departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True)
    destino_oficina = models.ForeignKey(Oficina, on_delete=models.SET_NULL, null=True, blank=True)
    
    estado = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nuevo Estado")
    observacion = models.TextField(max_length=2000, blank=True, null=True, verbose_name="Nota de Pase")
    usuario_emisor = models.CharField(max_length=100, blank=True, null=True, verbose_name="Enviado por")

    class Meta:
        verbose_name = "Pase de Expediente"
        verbose_name_plural = "Historial de Pases"
        ordering = ['-fecha_pase']

    def __str__(self):
        return f"Pase de {self.expediente.nro_expediente} emitido el {self.fecha_pase.strftime('%d/%m/%Y %H:%M')}"
