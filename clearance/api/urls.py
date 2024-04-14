from django.urls import path
from clearance.api import views
urlpatterns = [
    path('departments/', views.DeparmentList.as_view(), name='departments'),
    path('departments/entities/', views.dept_entities, name='dept_entities'),
    path('userinfo/', views.get_userinfo, name='userinfo'),
    path('apply/', views.apply_for_clearance, name='apply_for_clearance'),
    path('dashboard-clearances/', views.dashboard_clearance_requests, name='dashboard_clearance_requests'),
    path('section-clearances/', views.section_clearance, name='section_clearances'),
    path('approve/<str:modelname>/<int:pk>/', views.approve_clearance_entity, name='approve_clearance_entity'),
    path('archive/<str:modelname>/<int:pk>/', views.archive_clearance_entity, name='archive_clearance_entity'),
    path('unarchive/<str:modelname>/<int:pk>/', views.unarchive_clearance_entity, name='unarchive_clearance_entity'),
]
