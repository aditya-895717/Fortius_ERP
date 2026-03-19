"""
Accounts Models
===============
Department, Role, and UserProfile models for role-based access control.
"""
from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    """Organizational department (HR, Engineering, Sales, etc.)."""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Role(models.Model):
    """User role that determines dashboard and module access."""
    ROLE_CHOICES = [
        ('admin', 'Admin / Super Admin'),
        ('hr', 'Human Resources'),
        ('tpm', 'Technical Project Manager'),
        ('finance', 'Finance'),
        ('sales', 'Sales'),
        ('engineering', 'Engineering'),
        ('procurement', 'Procurement'),
    ]
    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.get_name_display()


class UserProfile(models.Model):
    """Extended user profile linked to Django User via OneToOneField."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
        ('terminated', 'Terminated'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    reporting_manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='direct_reports'
    )
    designation = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.employee_id or 'N/A'})"

    @property
    def role_name(self):
        """Return the role key string (e.g. 'hr', 'tpm', 'admin')."""
        return self.role.name if self.role else None
