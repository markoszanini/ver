import os
import django
import sys
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from expedientes.models import Expediente
from organigrama.models import Funcionario

def debug_render():
    try:
        user = User.objects.get(username='mariana.martinez')
        rf = RequestFactory()
        request = rf.get('/expedientes/mesa/dashboard/')
        request.user = user
        request._messages = FallbackStorage(request)
        
        # Manually assemble context like the view does
        funcionario = getattr(user, 'funcionario_link', None)
        por_confirmar = Expediente.objects.filter(confirmado=False).order_by('-fecha_ingreso')
        depto_mesa = funcionario.departamento
        en_tramite = Expediente.objects.filter(actual_departamento=depto_mesa, confirmado=True).exclude(estado__in=['Resuelto', 'Archivado', 'Finalizado']).order_by('-fecha_ingreso')
        
        context = {
            'por_confirmar': por_confirmar,
            'en_tramite': en_tramite,
            'funcionario': funcionario,
            'request': request,
            'user': user,
            'is_mesa_staff': True, # simulating context processor
            'unread_expediente_count': 1
        }
        
        print("Attempting to render mesa_dashboard.html...")
        html = render_to_string('expedientes/mesa_dashboard.html', context, request=request)
        print("Render Success!")
        # print(html[:500])
    except Exception:
        print("RENDER FAILED:")
        traceback.print_exc()

if __name__ == '__main__':
    debug_render()
