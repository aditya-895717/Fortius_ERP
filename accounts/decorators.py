"""
Role-Based Access Decorators
=============================
Decorators to restrict view access by user role.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*allowed_roles):
    """
    Decorator to restrict access to users with specific roles.
    Admin role always has access. Usage: @role_required('hr', 'admin')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            # Superusers always have access
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            # Check user profile and role
            profile = getattr(request.user, 'profile', None)
            if profile and profile.role:
                user_role = profile.role.name
                if user_role in allowed_roles or 'admin' == user_role:
                    return view_func(request, *args, **kwargs)
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('core:access_denied')
        return wrapper
    return decorator


def admin_required(view_func):
    """Shortcut decorator for admin-only views."""
    return role_required('admin')(view_func)


def hr_required(view_func):
    """Shortcut decorator for HR-only views."""
    return role_required('hr', 'admin')(view_func)


def tpm_required(view_func):
    """Shortcut decorator for TPM-only views."""
    return role_required('tpm', 'admin')(view_func)
