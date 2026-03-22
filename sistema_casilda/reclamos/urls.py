from django.urls import path
from . import views

app_name = 'reclamos'

urlpatterns = [
    path('', views.mis_reclamos, name='mis_reclamos'),
    path('nuevo/', views.nuevo_reclamo, name='nuevo_reclamo'),
    path('<int:reclamo_id>/', views.detalle_reclamo, name='detalle_reclamo'),
    path('api/unread_count/', views.admin_unread_count, name='admin_unread_count'),
]
