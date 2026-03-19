"""
Employee Portal Views
=====================
Views for self-service actions: dashboard, leaves, grievance, profile, resignation.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import LeaveRequestForm, GrievanceForm, ResignationForm
from hr.models import LeaveRequest, Grievance, ExitRecord, Attendance, LeaveBalance
from accounts.models import UserProfile
from core.models import ActivityLog
from workflows.services import WorkflowService

@login_required
def dashboard(request):
    """Employee personal dashboard."""
    today = timezone.now().date()
    profile = getattr(request.user, 'profile', None)
    
    context = {
        'profile': profile,
        'recent_leaves': LeaveRequest.objects.filter(employee=request.user).order_by('-applied_on')[:5],
        'recent_attendance': Attendance.objects.filter(employee=request.user).order_by('-date')[:5],
        'leave_balances': LeaveBalance.objects.filter(employee=request.user, year=today.year),
    }
    
    # Check if there's an active resignation
    resignation = ExitRecord.objects.filter(employee=request.user).first()
    context['resignation'] = resignation
    
    return render(request, 'employee_portal/dashboard.html', context)


@login_required
def profile_view(request):
    """View basic profile."""
    profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'employee_portal/profile.html', {'profile': profile})


@login_required
def leave_list(request):
    """List employee leaves."""
    leaves = LeaveRequest.objects.filter(employee=request.user).order_by('-applied_on')
    return render(request, 'employee_portal/leave_list.html', {'leaves': leaves})


@login_required
def leave_apply(request):
    """Apply for leave."""
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = request.user
            leave.save()
            
            # Use Workflow Service to record the initial submission action
            WorkflowService.add_action(leave, 'submitted', request.user, "Leave application submitted")
            
            # Send Notification
            from core.services import EmailNotificationService
            if getattr(leave.employee, 'profile', None) and leave.employee.profile.reporting_manager:
                manager = leave.employee.profile.reporting_manager
                EmailNotificationService.send_and_create_notification(
                    user=manager,
                    title="New Leave Request",
                    message=f"{request.user.get_full_name()} has applied for leave from {leave.start_date} to {leave.end_date}.",
                    level="info",
                    link=f"/hr/leaves/{leave.id}/"
                )
            
            ActivityLog.objects.create(
                user=request.user, action='create', model_name='LeaveRequest', 
                object_id=leave.id, object_repr=str(leave), details="Applied for leave"
            )
            messages.success(request, 'Leave request submitted successfully.')
            return redirect('employee_portal:leave_list')
    else:
        form = LeaveRequestForm()
        
    return render(request, 'employee_portal/leave_apply.html', {'form': form})


@login_required
def grievance_list(request):
    """List grievances."""
    grievances = Grievance.objects.filter(employee=request.user).order_by('-filed_date')
    return render(request, 'employee_portal/grievance_list.html', {'grievances': grievances})


@login_required
def grievance_submit(request):
    """Submit a grievance."""
    if request.method == 'POST':
        form = GrievanceForm(request.POST)
        if form.is_valid():
            grievance = form.save(commit=False)
            grievance.employee = request.user
            grievance.save()
            messages.success(request, 'Grievance submitted successfully.')
            return redirect('employee_portal:grievance_list')
    else:
        form = GrievanceForm()
    return render(request, 'employee_portal/grievance_submit.html', {'form': form})


@login_required
def resignation_view(request):
    """View resignation status."""
    resignation = ExitRecord.objects.filter(employee=request.user).first()
    return render(request, 'employee_portal/resignation_view.html', {'resignation': resignation})


@login_required
def resignation_submit(request):
    """Submit a resignation."""
    # Check if already resigned
    existing = ExitRecord.objects.filter(employee=request.user).first()
    if existing:
        messages.warning(request, 'You already have an active resignation/exit record.')
        return redirect('employee_portal:resignation_view')
        
    if request.method == 'POST':
        form = ResignationForm(request.POST)
        if form.is_valid():
            exit_record = form.save(commit=False)
            exit_record.employee = request.user
            exit_record.save()
            
            # Workflow tracking
            WorkflowService.add_action(exit_record, 'submitted', request.user, "Resignation submitted via portal")
            
            # Notify HR Admins
            from core.services import EmailNotificationService
            from django.contrib.auth.models import User
            hr_users = User.objects.filter(profile__role__name='hr')
            for hr in hr_users:
                EmailNotificationService.send_and_create_notification(
                    user=hr,
                    title="Resignation Submitted",
                    message=f"{request.user.get_full_name()} has submitted their resignation.",
                    level="warning",
                    link=f"/hr/exits/{exit_record.id}/"
                )
                
            messages.success(request, 'Your resignation request has been submitted to HR.')
            return redirect('employee_portal:resignation_view')
    else:
        form = ResignationForm()
    
    return render(request, 'employee_portal/resignation_submit.html', {'form': form})
