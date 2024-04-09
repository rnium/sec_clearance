from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('api/login/', views.api_login, name='api_login'),
    path('pendingstudents/', views.PendingStudents.as_view(), name='pending_students'),
    path('approve-studentac/<int:registration>/', views.approve_student_ac, name='approve_studentac'),
    path('delete-studentac/<int:registration>/', views.DeleteStudentAc.as_view(), name='delete_studentac'),
    path('student/signup/', views.student_signup, name='student_signup'),
    path('student/updateprofile/', views.student_profile_update, name='student_profile_update'),
    path('progressive-studentinfo/', views.progressive_studentinfo, name='progressive_studentinfo'),
]
