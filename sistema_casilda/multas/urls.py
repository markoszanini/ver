from django.urls import path
from . import views

app_name = 'multas'

urlpatterns = [
    path('', views.index_consultas, name='index_consultas'),
    path('consulta/<str:tipo_consulta>/', views.consulta_publica, name='consulta_publica'),
    path('consulta/', views.consulta_publica, name='consulta_publica_general'),
    path('libre-de-deuda/pdf/', views.libre_deuda_pdf, name='libre_deuda_pdf'),
    path('acta/<int:id_acta>/pdf/', views.acta_pdf, name='acta_pdf'),
    path('acta/<int:id_acta>/pagar/', views.pagar_acta, name='pagar_acta'),
]
