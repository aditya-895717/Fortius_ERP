"""
Core Views
==========
Dashboard router, role-based dashboards, notification and activity log views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count, Q

from .models import Notification, ActivityLog
from accounts.models import Department, UserProfile
from accounts.decorators import admin_required


# ---------------------------------------------------------------------------
# Dashboard Router
# ---------------------------------------------------------------------------

@login_required
def dashboard_router(request):
    """Redirect user to their role-specific dashboard."""
    profile = getattr(request.user, 'profile', None)
    if request.user.is_superuser or (profile and profile.role and profile.role.name == 'admin'):
        return redirect('core:admin_dashboard')
    elif profile and profile.role:
        role = profile.role.name
        if role == 'hr':
            return redirect('core:hr_dashboard')
        elif role == 'tpm':
            return redirect('core:tpm_dashboard')
        else:
            # Default for employee or any other role
            return redirect('employee_portal:dashboard')
    # Default fallback
    return redirect('employee_portal:dashboard')


# ---------------------------------------------------------------------------
# Admin Dashboard
# ---------------------------------------------------------------------------

@login_required
@admin_required
def admin_dashboard(request):
    """Admin overview dashboard with system stats."""
    today = timezone.now().date()

    context = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'total_departments': Department.objects.filter(is_active=True).count(),
        'recent_activities': ActivityLog.objects.select_related('user')[:10],
        'users_by_role': UserProfile.objects.values('role__name').annotate(
            count=Count('id')).order_by('-count'),
        'users_by_dept': UserProfile.objects.filter(
            department__isnull=False
        ).values('department__name').annotate(count=Count('id')).order_by('-count'),
    }

    # Try to get HR/TPM stats
    try:
        from hr.models import LeaveRequest, JobOpening, Attendance
        context['pending_leaves'] = LeaveRequest.objects.filter(status='pending').count()
        context['open_positions'] = JobOpening.objects.filter(status='open').count()
        context['today_attendance'] = Attendance.objects.filter(date=today).count()
    except Exception:
        pass

    try:
        from tpm.models import Project, Task
        context['active_projects'] = Project.objects.filter(status='active').count()
        context['total_tasks'] = Task.objects.count()
        context['overdue_tasks'] = Task.objects.filter(
            due_date__lt=today, status__in=['todo', 'in_progress', 'review']
        ).count()
    except Exception:
        pass

    return render(request, 'core/admin_dashboard.html', context)


# ---------------------------------------------------------------------------
# HR Dashboard
# ---------------------------------------------------------------------------

@login_required
def hr_dashboard(request):
    """HR dashboard with employee and HR stats."""
    from hr.models import (
        Attendance, LeaveRequest, JobOpening, Candidate,
        TrainingSession, Grievance, ExitRecord
    )
    today = timezone.now().date()

    context = {
        'total_employees': UserProfile.objects.filter(status='active').count(),
        'total_departments': Department.objects.filter(is_active=True).count(),
        'today_present': Attendance.objects.filter(date=today, status='present').count(),
        'today_absent': Attendance.objects.filter(date=today, status='absent').count(),
        'pending_leaves': LeaveRequest.objects.filter(status='pending').count(),
        'approved_leaves': LeaveRequest.objects.filter(
            status='approved', start_date__lte=today, end_date__gte=today
        ).count(),
        'open_positions': JobOpening.objects.filter(status='open').count(),
        'total_candidates': Candidate.objects.filter(
            status__in=['applied', 'shortlisted', 'interview']
        ).count(),
        'active_trainings': TrainingSession.objects.filter(
            status__in=['upcoming', 'ongoing']
        ).count(),
        'open_grievances': Grievance.objects.filter(
            status__in=['open', 'in_progress']
        ).count(),
        'active_exits': ExitRecord.objects.filter(
            status__in=['initiated', 'notice_period', 'exit_interview']
        ).count(),
        'recent_leaves': LeaveRequest.objects.select_related(
            'employee', 'leave_type'
        ).order_by('-applied_on')[:5],
        'dept_employee_count': UserProfile.objects.filter(
            department__isnull=False, status='active'
        ).values('department__name').annotate(count=Count('id')).order_by('-count'),
    }
    return render(request, 'core/hr_dashboard.html', context)


# ---------------------------------------------------------------------------
# TPM Dashboard
# ---------------------------------------------------------------------------

@login_required
def tpm_dashboard(request):
    """TPM dashboard with project and task stats."""
    from tpm.models import Project, Task, Risk, Issue, Milestone
    today = timezone.now().date()
    week_end = today + timezone.timedelta(days=7)

    context = {
        'active_projects': Project.objects.filter(status='active').count(),
        'total_projects': Project.objects.count(),
        'completed_projects': Project.objects.filter(status='completed').count(),
        'total_tasks': Task.objects.count(),
        'overdue_tasks': Task.objects.filter(
            due_date__lt=today, status__in=['todo', 'in_progress', 'review']
        ).count(),
        'tasks_due_this_week': Task.objects.filter(
            due_date__range=[today, week_end],
            status__in=['todo', 'in_progress', 'review']
        ).count(),
        'high_risks': Risk.objects.filter(
            severity__in=['high', 'critical'], status__in=['identified', 'mitigating']
        ).count(),
        'open_issues': Issue.objects.filter(status__in=['open', 'in_progress']).count(),
        'recent_projects': Project.objects.order_by('-updated_at')[:5],
        'upcoming_milestones': Milestone.objects.filter(
            is_completed=False, due_date__gte=today
        ).order_by('due_date')[:5],
        'project_status_summary': Project.objects.values('status').annotate(
            count=Count('id')
        ),
    }
    return render(request, 'core/tpm_dashboard.html', context)


# ---------------------------------------------------------------------------
# Shared Views
# ---------------------------------------------------------------------------

@login_required
def access_denied_view(request):
    """Access denied page for unauthorized access attempts."""
    return render(request, 'core/access_denied.html')


@login_required
def notifications_view(request):
    """View all notifications for the current user."""
    notifications = Notification.objects.filter(user=request.user)
    paginator = Paginator(notifications, 20)
    page = request.GET.get('page')
    notifications = paginator.get_page(page)
    return render(request, 'core/notifications.html', {'notifications': notifications})


@login_required
def mark_notification_read(request, pk):
    """Mark a single notification as read."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    if notification.link:
        return redirect(notification.link)
    return redirect('core:notifications')


@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('core:notifications')


@login_required
@admin_required
def activity_log_view(request):
    """View system activity log (admin only)."""
    logs = ActivityLog.objects.select_related('user').all()

    query = request.GET.get('q', '')
    if query:
        logs = logs.filter(
            Q(user__username__icontains=query) |
            Q(model_name__icontains=query) |
            Q(details__icontains=query)
        )

    action_filter = request.GET.get('action', '')
    if action_filter:
        logs = logs.filter(action=action_filter)

    paginator = Paginator(logs, 25)
    page = request.GET.get('page')
    logs = paginator.get_page(page)
    return render(request, 'core/activity_log.html', {
        'logs': logs,
        'query': query,
        'action_filter': action_filter,
    })
