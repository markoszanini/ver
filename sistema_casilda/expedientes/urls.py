from django.urls import path
from . import views

app_name = 'expedientes'

urlpatterns = [
    path('mis-expedientes/', views.mis_expedientes, name='mis_expedientes'),
    path('seguimiento/<int:id_expediente>/', views.seguimiento_expediente, name='seguimiento_expediente'),
]
