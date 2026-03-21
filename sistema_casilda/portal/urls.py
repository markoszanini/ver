from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('empleo/postular/', views.postular_empleo, name='postular_empleo'),
    path('ferias/registro/', views.registro_feriante, name='registro_feriante'),
]
