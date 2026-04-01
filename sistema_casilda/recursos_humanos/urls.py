from django.urls import path
from . import views

app_name = 'recursos_humanos'

urlpatterns = [
    path('mi-portal/', views.portal_empleado, name='portal_empleado'),
    path('mis-recibos/', views.mis_recibos, name='mis_recibos'),
    path('mis-vacaciones/', views.mis_vacaciones, name='mis_vacaciones'),
]
