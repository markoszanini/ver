from django.urls import path
from . import views

app_name = 'organigrama'
urlpatterns = [
    path('ajax/get_direcciones/', views.get_direcciones, name='get_direcciones'),
    path('ajax/get_departamentos/', views.get_departamentos, name='get_departamentos'),
    path('ajax/get_divisiones/', views.get_divisiones, name='get_divisiones'),
    path('ajax/get_subdivisiones/', views.get_subdivisiones, name='get_subdivisiones'),
    path('ajax/get_secciones/', views.get_secciones, name='get_secciones'),
    path('ajax/get_oficinas/', views.get_oficinas, name='get_oficinas'),
]
