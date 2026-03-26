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
    path('ferias/mis-ferias/', views.mis_ferias, name='mis_ferias'),
    path('ferias/inscribirse/<int:feria_id>/', views.inscribirse_feria, name='inscribirse_feria'),
    path('omic/', views.omic_view, name='omic'),
]
