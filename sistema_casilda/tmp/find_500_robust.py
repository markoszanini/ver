import os
import django
import sys
import traceback

# Add current directory to path to allow imports of core
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from expedientes.views import mesa_dashboard
from django.template.loader import render_to_string

def find_error():
    try:
        user = User.objects.get(username='mariana.martinez')
        rf = RequestFactory()
        request = rf.get('/expedientes/mesa/dashboard/')
        request.user = user
        request._messages = FallbackStorage(request)
        
        # Test context processor
        from expedientes.context_processors import unread_notifications
        ctx = unread_notifications(request)
        print(f"Context Processor Output: {ctx}")
        
        # Test view execution
        response = mesa_dashboard(request)
        print(f"View Status: {response.status_code}")
        
        # Force EVERYTHING to render!
        print("Starting full render...")
        if hasattr(response, 'render'):
            response.render()
        
        print("Rendering successful! No error caught in shell.")
    except Exception:
        print("TRACEBACK CAUGHT:")
        traceback.print_exc()

if __name__ == '__main__':
    find_error()
