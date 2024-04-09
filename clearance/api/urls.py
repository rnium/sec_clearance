from django.urls import path
from clearance.api import views
urlpatterns = [
    path('userinfo/', views.get_userinfo, name='userinfo'),
    path('apply/', views.apply_for_clearance, name='apply_for_clearance'),
]
