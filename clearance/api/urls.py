from django.urls import path
from clearance.api import views
urlpatterns = [
    path('userinfo/', views.get_userinfo, name='userinfo'),
]
