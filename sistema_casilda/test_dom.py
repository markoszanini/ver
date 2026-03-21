import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.test import Client
from django.contrib.auth.models import User
import re

c = Client()
u = User.objects.get(username='test_admin123')
c.login(username='test_admin123', password='pass')

response = c.get('/admin/empleo/postulante/add/', HTTP_HOST='localhost')
html = response.content.decode('utf-8')

print("ALL SELECT IDs IN HTML:")
for select in re.findall(r'<select[^>]*id="([^"]*)"[^>]*>', html):
    print(" -", select)
