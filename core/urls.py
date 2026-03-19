"""
Core URL Configuration
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard router
    path('', views.dashboard_router, name='dashboard'),

    # Role-based dashboards
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/hr/', views.hr_dashboard, name='hr_dashboard'),
    path('dashboard/tpm/', views.tpm_dashboard, name='tpm_dashboard'),

    # Shared pages
    path('access-denied/', views.access_denied_view, name='access_denied'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_read'),
    path('activity-log/', views.activity_log_view, name='activity_log'),
]
