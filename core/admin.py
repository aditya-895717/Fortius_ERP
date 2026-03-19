"""
Core Admin
"""
from django.contrib import admin
from .models import Notification, ActivityLog


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'level', 'is_read', 'created_at']
    list_filter = ['level', 'is_read']
    search_fields = ['title', 'user__username']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_repr', 'timestamp']
    list_filter = ['action', 'model_name']
    search_fields = ['user__username', 'model_name', 'details']
