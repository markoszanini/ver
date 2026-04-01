from django.urls import path
from . import views

app_name = 'capacitaciones'

urlpatterns = [
    path('', views.explorar_capacitaciones, name='explorar'),
    path('mis-capacitaciones/', views.mis_capacitaciones, name='mis_capacitaciones'),
    path('inscribirse/<int:cap_id>/', views.inscribirse_curso, name='inscribirse_curso'),
    path('certificado/<int:insc_id>/', views.descargar_certificado, name='descargar_certificado'),
]
