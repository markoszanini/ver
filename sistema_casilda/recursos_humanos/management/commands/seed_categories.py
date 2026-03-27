from django.core.management.base import BaseCommand
from recursos_humanos.models import CategoriaSalarial

class Command(BaseCommand):
    help = 'Carga las categorías salariales de la 8 a la 22 según Decreto 2695'

    def handle(self, *args, **options):
        # Valores aproximados para iniciar, el usuario los ajustará en el admin
        # En una implementación real, estos vendrían de una tabla de escala salarial
        base_amount = 400000  # Ejemplo base para cat 8
        increment = 15000     # Incremento base por categoría
        
        for i in range(8, 23):
            cat_name = f"Categoría {i}"
            sueldo = base_amount + (i - 8) * increment
            
            obj, created = CategoriaSalarial.objects.get_or_create(
                nombre=cat_name,
                defaults={'sueldo_basico': sueldo}
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Creada {cat_name} con sueldo {sueldo}'))
            else:
                self.stdout.write(self.style.WARNING(f'{cat_name} ya existe'))
