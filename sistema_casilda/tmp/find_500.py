import os
import django
import sys
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from expedientes.views import mesa_dashboard

def find_error():
    try:
        user = User.objects.get(username='mariana.martinez')
        rf = RequestFactory()
        request = rf.get('/expedientes/mesa/dashboard/')
        request.user = user
        request._messages = FallbackStorage(request)
        
        # Test context processor since it's global
        from expedientes.context_processors import unread_notifications
        ctx = unread_notifications(request)
        print(f"Context Processor Output: {ctx}")
        
        # Test view execution
        response = mesa_dashboard(request)
        print(f"View Status: {response.status_code}")
        
        # Force template rendering if it's a TemplateResponse
        if hasattr(response, 'render'):
            response.render()
        print("Rendering successful!")
    except Exception:
        print("TRACEBACK CAUGHT:")
        traceback.print_exc()

if __name__ == '__main__':
    find_error()
