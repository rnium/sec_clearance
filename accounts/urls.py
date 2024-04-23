from django.urls import path, re_path
from accounts import views
from django.views.generic import TemplateView


app_name = 'accounts'

urlpatterns = [
    path('validate-token/', views.validate_token, name='validate_token'),
    path('recovery/<str:uid>/<str:token>/', TemplateView.as_view(template_name='main_site/index.html'), name='reset_password_form'),
    path('resetpassoword/', views.reset_password, name='reset_password'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('resetpassoword/', views.reset_password, name='reset_password'),
    path('sendrecoverymail/', views.send_recovery_email, name='send_recovery_email'),
    path('api/admin/signup/', views.admin_signup, name='admin_signup'),
    path('pendingstudents/', views.PendingStudents.as_view(), name='pending_students'),
    path('studentac/approve/', views.approve_student_ac, name='approve_studentac'),
    path('studentac/approveall/', views.approve_all_student_ac, name='approve_all_student_ac'),
    path('studentac/delete/', views.delete_student_ac, name='delete_studentac'),
    path('student/signup/', views.student_signup, name='student_signup'),
    path('student/updateprofile/', views.student_profile_update, name='student_profile_update'),
    path('admin/updateprofile/', views.admin_profile_update, name='admin_profile_update'),
    path('progressive-studentinfo/', views.progressive_studentinfo, name='progressive_studentinfo'),
    path('admin-roles/', views.admin_roles, name='admin_roles'),
    path('members/', views.members, name='members'),
    path('members/sendinvite/', views.send_invitation, name='send_invitation'),
    path('members/search/', views.search_member, name='search_member'),
    path('members/changedept/', views.change_dept, name='change_dept'),
    path('members/delete/', views.delete_account, name='delete_account'),

]
