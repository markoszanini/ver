from django.urls import path
from . import views

app_name = 'expedientes'

urlpatterns = [
    path('mis-expedientes/', views.mis_expedientes, name='mis_expedientes'),
    path('mis-expedientes-internos/', views.mis_expedientes_internos, name='mis_expedientes_internos'),
    path('iniciar/', views.iniciar_expediente_staff, name='iniciar_expediente_staff'),
    path('seguimiento/<int:id_expediente>/', views.seguimiento_expediente, name='seguimiento_expediente'),
]
