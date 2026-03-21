from django.urls import path
from . import views

app_name = 'empleo'
urlpatterns = [
    path('perfiles-cv/', views.perfiles_cv, name='perfiles_cv'),
    path('ajax/puestos/', views.ajax_get_puestos, name='ajax_puestos'),
]
