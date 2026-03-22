import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from reclamos.views import mis_reclamos

# Create a temporary user without a vecino profile
user, created = User.objects.get_or_create(username='test_no_vecino')

factory = RequestFactory()
request = factory.get('/reclamos/')
request.user = user

try:
    response = mis_reclamos(request)
    print("Response status:", response.status_code)
except Exception as e:
    import traceback
    traceback.print_exc()
