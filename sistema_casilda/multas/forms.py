from django import forms
from .models import Acta, Persona, Vehiculo, Inmueble, Animal

class ActaAdminForm(forms.ModelForm):
    # Persona
    pers_dni = forms.CharField(max_length=20, label="DNI", required=True)
    pers_nombre = forms.CharField(max_length=100, label="Nombre", required=True)
    pers_apellido = forms.CharField(max_length=100, label="Apellido", required=True)
    pers_fecha_nacimiento = forms.DateField(label="Fecha Nacimiento", required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    pers_localidad = forms.CharField(max_length=100, label="Localidad", required=False)
    pers_calle = forms.CharField(max_length=100, label="Calle", required=False)
    pers_numero = forms.CharField(max_length=10, label="Número", required=False)
    pers_codigo_postal = forms.CharField(max_length=10, label="Cod. Postal", required=False)
    pers_telefono = forms.CharField(max_length=30, label="Teléfono", required=False)
    pers_correo = forms.EmailField(max_length=100, label="Correo", required=False)

    # Vehiculo
    veh_patente = forms.CharField(max_length=20, label="Patente", required=False)
    veh_marca = forms.CharField(max_length=50, label="Marca", required=False)
    veh_modelo = forms.CharField(max_length=50, label="Modelo", required=False)
    veh_color = forms.CharField(max_length=30, label="Color", required=False)
    veh_tipo_vehiculo = forms.CharField(max_length=50, label="Tipo Vehículo", required=False)
    veh_categoria = forms.CharField(max_length=50, label="Categoría", required=False)
    veh_anio_fabricacion = forms.IntegerField(label="Año Fabric.", required=False)

    # Animal
    ani_raza = forms.CharField(max_length=50, label="Raza", required=False)
    ani_especie = forms.CharField(max_length=50, label="Especie", required=False)
    ani_sexo = forms.CharField(max_length=10, label="Sexo", required=False)

    # Inmueble
    inm_nomenclatura = forms.CharField(max_length=50, label="Nomenclatura", required=False)
    inm_cuil = forms.CharField(max_length=20, label="CUIL", required=False)
    inm_razon_social = forms.CharField(max_length=100, label="Razón Social", required=False)
    inm_calle = forms.CharField(max_length=100, label="Calle", required=False)
    inm_numero = forms.CharField(max_length=10, label="Número", required=False)
    inm_manzana = forms.CharField(max_length=10, label="Manzana", required=False)
    inm_seccion = forms.CharField(max_length=10, label="Sección", required=False)
    inm_parcela = forms.CharField(max_length=10, label="Parcela", required=False)
    inm_tipo_inmueble = forms.CharField(max_length=50, label="Tipo", required=False)
    inm_uso_inmueble = forms.CharField(max_length=50, label="Uso", required=False)
    inm_metros_cuadrados = forms.DecimalField(max_digits=10, decimal_places=2, label="Metros Cuadrados", required=False)

    class Meta:
        model = Acta
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            virtual_fields = [
                'pers_dni', 'pers_nombre', 'pers_apellido', 'pers_fecha_nacimiento',
                'pers_localidad', 'pers_calle', 'pers_numero', 'pers_codigo_postal', 'pers_telefono', 'pers_correo',
                'veh_patente', 'veh_marca', 'veh_modelo', 'veh_color', 'veh_tipo_vehiculo', 'veh_categoria', 'veh_anio_fabricacion',
                'ani_raza', 'ani_especie', 'ani_sexo',
                'inm_nomenclatura', 'inm_cuil', 'inm_razon_social', 'inm_calle', 'inm_numero', 'inm_manzana', 'inm_seccion', 'inm_parcela', 'inm_tipo_inmueble', 'inm_uso_inmueble', 'inm_metros_cuadrados'
            ]
            for f in virtual_fields:
                self.fields[f].disabled = True
            
            if self.instance.persona:
                self.initial['pers_dni'] = self.instance.persona.dni
                self.initial['pers_nombre'] = self.instance.persona.nombre
                self.initial['pers_apellido'] = self.instance.persona.apellido
                self.initial['pers_fecha_nacimiento'] = self.instance.persona.fecha_nacimiento
                self.initial['pers_localidad'] = self.instance.persona.localidad
                self.initial['pers_calle'] = self.instance.persona.calle
                self.initial['pers_numero'] = self.instance.persona.numero
                self.initial['pers_codigo_postal'] = self.instance.persona.codigo_postal
                self.initial['pers_telefono'] = self.instance.persona.telefono
                self.initial['pers_correo'] = self.instance.persona.correo
            if self.instance.vehiculo:
                self.initial['veh_patente'] = self.instance.vehiculo.patente
                self.initial['veh_marca'] = self.instance.vehiculo.marca
                self.initial['veh_modelo'] = self.instance.vehiculo.modelo
                self.initial['veh_color'] = self.instance.vehiculo.color
                self.initial['veh_tipo_vehiculo'] = self.instance.vehiculo.tipo_vehiculo
                self.initial['veh_categoria'] = self.instance.vehiculo.categoria
                self.initial['veh_anio_fabricacion'] = self.instance.vehiculo.anio_fabricacion
            if self.instance.animal:
                self.initial['ani_raza'] = self.instance.animal.raza
                self.initial['ani_especie'] = self.instance.animal.especie
                self.initial['ani_sexo'] = self.instance.animal.sexo
            if self.instance.inmueble:
                self.initial['inm_nomenclatura'] = self.instance.inmueble.nomenclatura
                self.initial['inm_cuil'] = self.instance.inmueble.cuil
                self.initial['inm_razon_social'] = self.instance.inmueble.razon_social
                self.initial['inm_calle'] = self.instance.inmueble.calle
                self.initial['inm_numero'] = self.instance.inmueble.numero
                self.initial['inm_manzana'] = self.instance.inmueble.manzana
                self.initial['inm_seccion'] = self.instance.inmueble.seccion
                self.initial['inm_parcela'] = self.instance.inmueble.parcela
                self.initial['inm_tipo_inmueble'] = self.instance.inmueble.tipo_inmueble
                self.initial['inm_uso_inmueble'] = self.instance.inmueble.uso_inmueble
                self.initial['inm_metros_cuadrados'] = self.instance.inmueble.metros_cuadrados

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo_acta')
        if tipo == 'VEHICULO' and not cleaned_data.get('veh_patente'):
            self.add_error('veh_patente', 'La patente es obligatoria para actas de vehículo.')
        if tipo == 'INMUEBLE' and not cleaned_data.get('inm_nomenclatura'):
            self.add_error('inm_nomenclatura', 'La nomenclatura es obligatoria para actas de inmueble.')
        return cleaned_data
