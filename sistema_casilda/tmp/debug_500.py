import os
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from expedientes.views import mesa_dashboard

def debug():
    try:
        user = User.objects.get(username='mariana.martinez')
        rf = RequestFactory()
        request = rf.get('/expedientes/mesa/dashboard/')
        request.user = user
        request._messages = FallbackStorage(request)
        
        # Test context processor as well
        from expedientes.context_processors import unread_notifications
        print("Testing context processor...")
        ctx = unread_notifications(request)
        print(f"Context: {ctx}")
        
        print("Testing view rendering...")
        response = mesa_dashboard(request)
        print(f"Status: {response.status_code}")
        # Force rendering if it's a TemplateResponse
        if hasattr(response, 'render'):
            response.render()
        print("Rendering successful")
    except Exception:
        traceback.print_exc()

if __name__ == '__main__':
    debug()
