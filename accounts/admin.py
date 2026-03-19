"""
Accounts Admin
"""
from django.contrib import admin
from .models import Department, Role, UserProfile


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'role', 'department', 'status']
    list_filter = ['role', 'department', 'status']
    search_fields = ['user__username', 'user__first_name', 'employee_id']
