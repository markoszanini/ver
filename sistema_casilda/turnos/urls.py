from django.urls import path
from . import views

app_name = 'turnos'

urlpatterns = [
    path('', views.mis_turnos, name='mis_turnos'),
    path('solicitar/', views.solicitar_turno, name='solicitar_turno'),
    path('api/horarios/', views.api_horarios_disponibles, name='api_horarios_disponibles'),
]
