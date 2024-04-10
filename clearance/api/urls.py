from django.urls import path
from clearance.api import views
urlpatterns = [
    path('userinfo/', views.get_userinfo, name='userinfo'),
    path('apply/', views.apply_for_clearance, name='apply_for_clearance'),
    path('dashboard-clearances/', views.dashboard_clearance_requests, name='dashboard_clearance_requests'),
    path('approve/<str:modelname>/<int:pk>/', views.approve_clearance_entity, name='approve_clearance_entity'),
    path('archive/<str:modelname>/<int:pk>/', views.archive_clearance_entity, name='archive_clearance_entity'),
]
