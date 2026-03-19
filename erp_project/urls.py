"""
ERP Project URL Configuration
==============================
Routes to all app URL confs and serves media files in development.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('hr/', include('hr.urls')),
    path('tpm/', include('tpm.urls')),
    path('employee/', include('employee_portal.urls')),
    path('workflows/', include('workflows.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
