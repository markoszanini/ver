from django.urls import path
from . import views

app_name = 'ferias'
urlpatterns = [
    path('ajax/subrubros/', views.ajax_get_subrubros, name='ajax_subrubros'),
]
