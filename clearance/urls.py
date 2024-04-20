from django.urls import path, include
from clearance import views
app_name = 'clearance'

urlpatterns = [
    path('api/', include('clearance.api.urls')),
    path('report/download/', views.download_clearance_report, name='download_report'),
    path('verify/<str:b64_code>/', views.verify_clearance, name='verify_clearance'),
]
