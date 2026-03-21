import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from empleo.models import RubroEmpleo, PuestoEmpleo

print("Rubros en DB:", RubroEmpleo.objects.count())
print("Puestos en DB:", PuestoEmpleo.objects.count())
print("Puestos de Rubro 2:", PuestoEmpleo.objects.filter(rubro_id=2).count())

# test client
c = Client()
try:
    u = User.objects.get(username='test_admin123')
except User.DoesNotExist:
    u = User.objects.create_superuser('test_admin123', 'a@a.com', 'pass')

c.login(username='test_admin123', password='pass')

response = c.get('/empleo/ajax/puestos/', {'rubro_id': 2}, HTTP_HOST='localhost')
print("STATUS:", response.status_code)
print("CONTENT:", response.content.decode('utf-8'))
