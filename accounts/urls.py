from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('api/login/', views.api_login, name='api_login'),
    path('pendingstudents/', views.PendingStudents.as_view(), name='pending_students'),
    path('studentac/approve/', views.approve_student_ac, name='approve_studentac'),
    path('studentac/delete/', views.delete_student_ac, name='delete_studentac'),
    path('student/signup/', views.student_signup, name='student_signup'),
    path('student/updateprofile/', views.student_profile_update, name='student_profile_update'),
    path('progressive-studentinfo/', views.progressive_studentinfo, name='progressive_studentinfo'),
    path('admin-roles/', views.admin_roles, name='admin_roles'),
    path('members/', views.members, name='members'),
    path('members/sendinvite/', views.send_invitation, name='send_invitation'),

]
