from django.urls import path
from . import views

app_name = 'apicultura'
urlpatterns = [
    path('dashboard/', views.dashboard_apicultura, name='dashboard'),
    path('generar-informe/', views.generar_informe, name='generar_informe'),
]
