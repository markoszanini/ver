from django.urls import path
from . import views

app_name = 'impuestos'

urlpatterns = [
    path('', views.mis_impuestos, name='mis_impuestos'),
    path('cuenta/<int:impuesto_id>/', views.estado_cuenta, name='estado_cuenta'),
    path('deuda/<int:deuda_id>/pagar/', views.simular_pago, name='simular_pago'),
]
