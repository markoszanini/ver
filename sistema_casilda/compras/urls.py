from django.urls import path
from . import views

app_name = 'compras'

urlpatterns = [
    path('iniciar/', views.iniciar_oc_portal, name='iniciar_oc_portal'),
    path('mis-ordenes/', views.mis_ordenes_portal, name='mis_ordenes_portal'),
]
