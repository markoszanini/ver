from django.urls import path
from . import views, views_ajax

app_name = 'expedientes'

urlpatterns = [
    path('mis-expedientes/', views.mis_expedientes, name='mis_expedientes'),
    path('mis-expedientes-internos/', views.mis_expedientes_internos, name='mis_expedientes_internos'),
    path('iniciar/', views.iniciar_expediente_staff, name='iniciar_expediente_staff'),
    path('seguimiento/<int:id_expediente>/', views.seguimiento_expediente, name='seguimiento_expediente'),
    path('bandeja/', views.bandeja_entrada, name='bandeja_entrada'),
    path('procesar/<int:id_expediente>/', views.procesar_expediente, name='procesar_expediente'),
    
    # Mesa de Entrada
    path('mesa/dashboard/', views.mesa_dashboard, name='mesa_dashboard'),
    path('mesa/nuevo/', views.crear_expediente_mesa, name='crear_expediente_mesa'),
    path('mesa/confirmar/<int:id_expediente>/', views.confirmar_expediente_mesa, name='confirmar_expediente_mesa'),
    
    # AJAX Search
    path('ajax/buscar-destinos/', views_ajax.buscar_destinos_ajax, name='buscar_destinos_ajax'),
]


