from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('api/login/', views.api_login, name='api_login'),
]
