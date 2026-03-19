"""
Core Context Processors
=======================
Injects global context variables into all templates.
"""
from .models import Notification


def global_context(request):
    """Add role, notifications, and common data to all templates."""
    context = {}
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        context['user_role'] = profile.role.name if profile and profile.role else None
        context['user_role_display'] = profile.role.get_name_display() if profile and profile.role else 'No Role'
        context['user_profile'] = profile
        context['unread_notifications'] = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
    return context
