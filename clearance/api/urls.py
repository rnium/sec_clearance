from django.urls import path
from clearance.api import views
urlpatterns = [
    path('departments/', views.DeparmentList.as_view(), name='departments'),
    path('departments/sections/', views.dept_sections, name='dept_sections'),
    path('departments/sessions/', views.dept_sessions, name='dept_sessions'),
    path('sessions/students/', views.session_students, name='session_students'),
    path('sessions/add/', views.add_session, name='add_session'),
    path('userinfo/', views.get_userinfo, name='userinfo'),
    path('apply/', views.apply_for_clearance, name='apply_for_clearance'),
    path('dashboard-clearances/', views.dashboard_clearance_requests, name='dashboard_clearance_requests'),
    path('section-clearances/', views.section_clearance, name='section_clearances'),
    path('approve/<str:modelname>/<int:pk>/', views.approve_clearance_entity, name='approve_clearance_entity'),
    path('archive/<str:modelname>/<int:pk>/', views.archive_clearance_entity, name='archive_clearance_entity'),
    path('unarchive/<str:modelname>/<int:pk>/', views.unarchive_clearance_entity, name='unarchive_clearance_entity'),
    path('assignmember/', views.assign_member, name='assign_member'),
    path('unassign-member/', views.unassign_member, name='unassign_member'),
    path('remarks/', views.remarks, name='remarks'),
    path('clearanceinfo/', views.student_clearanceinfo, name='student_clearanceinfo'),
    path('clearanceinfo/adminview/', views.clearanceinfo_as_admin, name='clearanceinfo_as_admin'),
    path('remarksinfo/', views.student_remarks_info, name='student_remarks_info'),
]
