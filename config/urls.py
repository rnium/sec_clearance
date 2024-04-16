from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

exclude_prefixes = ['admin', 'static', 'media']
exclude_pattern = '|'.join(exclude_prefixes)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('clearance/', include('clearance.urls')),
    path('account/', include('accounts.urls')),
    re_path(rf'member-signup/', TemplateView.as_view(template_name='main_site/index.html'), name='signupadmin')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
urlpatterns.append(re_path(rf'.*', TemplateView.as_view(template_name='main_site/index.html')))
