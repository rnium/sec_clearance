from django.urls import path, include

app_name = 'clearance'

urlpatterns = [
    path('api/', include('clearance.api.urls')),
]
