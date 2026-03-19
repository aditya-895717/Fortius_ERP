"""
HR Views
========
Complete CRUD views for all HR modules with role-based access control.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q, Count

from accounts.decorators import hr_required
from accounts.models import UserProfile, Department
from core.models import ActivityLog
from .models import (
    Attendance, LeaveRequest, LeaveType, LeaveBalance,
    SalaryStructure, PayrollRecord, JobOpening, Candidate, Interview,
    Appraisal, TrainingSession, TrainingAssignment, Grievance, ExitRecord
)
from .forms import (
    AttendanceForm, LeaveRequestForm, LeaveActionForm, ExitActionForm,
    SalaryStructureForm, JobOpeningForm, CandidateForm, InterviewForm,
    AppraisalForm, TrainingSessionForm, TrainingAssignmentForm,
    GrievanceForm, GrievanceUpdateForm, ExitRecordForm
)
from workflows.services import WorkflowService
from core.services import EmailNotificationService

ITEMS = 15  # Items per page


# ===========================================================================
# EMPLOYEE DIRECTORY
# ===========================================================================

@login_required
@hr_required
def employee_list(request):
    """Employee directory with search and filters."""
    employees = UserProfile.objects.select_related(
        'user', 'role', 'department'
    ).all()

    q = request.GET.get('q', '')
    if q:
        employees = employees.filter(
            Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q) |
            Q(user__email__icontains=q) | Q(employee_id__icontains=q)
        )

    dept = request.GET.get('department', '')
    if dept:
        employees = employees.filter(department_id=dept)

    status = request.GET.get('status', '')
    if status:
        employees = employees.filter(status=status)

    paginator = Paginator(employees, ITEMS)
    employees = paginator.get_page(request.GET.get('page'))

    return render(request, 'hr/employee_list.html', {
        'employees': employees, 'query': q, 'dept_filter': dept, 'status_filter': status,
        'departments': Department.objects.filter(is_active=True),
    })


@login_required
@hr_required
def employee_detail(request, pk):
    """Employee detail page."""
    profile = get_object_or_404(UserProfile, pk=pk)
    return render(request, 'hr/employee_detail.html', {'profile': profile})


# ===========================================================================
# ATTENDANCE
# ===========================================================================

@login_required
@hr_required
def attendance_list(request):
    """View attendance records with date and employee filters."""
    records = Attendance.objects.select_related('employee').all()

    date_filter = request.GET.get('date', '')
    if date_filter:
        records = records.filter(date=date_filter)
    else:
        records = records.filter(date=timezone.now().date())

    q = request.GET.get('q', '')
    if q:
        records = records.filter(
            Q(employee__first_name__icontains=q) | Q(employee__last_name__icontains=q)
        )

    paginator = Paginator(records, ITEMS)
    records = paginator.get_page(request.GET.get('page'))

    return render(request, 'hr/attendance_list.html', {
        'records': records, 'date_filter': date_filter or timezone.now().date(), 'query': q,
    })


@login_required
@hr_required
def attendance_create(request):
    """Mark attendance for an employee."""
    form = AttendanceForm()
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            att = form.save(commit=False)
            att.marked_by = request.user
            att.save()
            messages.success(request, 'Attendance marked successfully.')
            return redirect('hr:attendance_list')
    return render(request, 'hr/generic_form.html', {
        'form': form, 'title': 'Mark Attendance', 'button_text': 'Save',
    })


@login_required
@hr_required
def attendance_edit(request, pk):
    """Edit an attendance record."""
    record = get_object_or_404(Attendance, pk=pk)
    form = AttendanceForm(instance=record)
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Attendance updated.')
            return redirect('hr:attendance_list')
    return render(request, 'hr/generic_form.html', {
        'form': form, 'title': 'Edit Attendance', 'button_text': 'Update',
    })


# ===========================================================================
# LEAVE MANAGEMENT
# ===========================================================================

@login_required
@hr_required
def leave_list(request):
    """List all leave requests with filters."""
    leaves = LeaveRequest.objects.select_related('employee', 'leave_type').all()

    status_filter = request.GET.get('status', '')
    if status_filter:
        leaves = leaves.filter(status=status_filter)

    q = request.GET.get('q', '')
    if q:
        leaves = leaves.filter(
            Q(employee__first_name__icontains=q) | Q(employee__last_name__icontains=q)
        )

    paginator = Paginator(leaves, ITEMS)
    leaves = paginator.get_page(request.GET.get('page'))

    return render(request, 'hr/leave_list.html', {
        'leaves': leaves, 'status_filter': status_filter, 'query': q,
    })


@login_required
@hr_required
def leave_create(request):
    """Apply for leave."""
    form = LeaveRequestForm()
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = request.user
            leave.save()
            messages.success(request, 'Leave request submitted.')
            return redirect('hr:leave_list')
    return render(request, 'hr/generic_form.html', {
        'form': form, 'title': 'Apply for Leave', 'button_text': 'Submit',
    })


@login_required
@hr_required
def leave_detail(request, pk):
    """Leave request detail with approve/reject."""
    leave = get_object_or_404(LeaveRequest, pk=pk)
    action_form = LeaveActionForm()

    if request.method == 'POST':
        action_form = LeaveActionForm(request.POST)
        if action_form.is_valid():
            action = action_form.cleaned_data['action']
            reason = action_form.cleaned_data.get('rejection_reason', '')
            
            try:
                if action == 'approved':
                    WorkflowService.approve_leave(leave, request.user, reason)
                    messages.success(request, 'Leave request approved.')
                    EmailNotificationService.send_and_create_notification(
                        user=leave.employee, title="Leave Approved",
                        message=f"Your leave from {leave.start_date} to {leave.end_date} has been approved.",
                        level="success", link=f"/portal/leaves/"
                    )
                elif action == 'rejected':
                    WorkflowService.reject_leave(leave, request.user, reason)
                    messages.success(request, 'Leave request rejected.')
                    EmailNotificationService.send_and_create_notification(
                        user=leave.employee, title="Leave Rejected",
                        message=f"Your leave from {leave.start_date} to {leave.end_date} was rejected. Reason: {reason}",
                        level="error", link=f"/portal/leaves/"
                    )
            except ValueError as e:
                messages.error(request, str(e))
                
            return redirect('hr:leave_list')

    return render(request, 'hr/leave_detail.html', {
        'leave': leave, 'action_form': action_form,
    })


# ===========================================================================
# PAYROLL
# ===========================================================================

@login_required
@hr_required
def salary_list(request):
    """List salary structures."""
    salaries = SalaryStructure.objects.select_related('employee').all()
    q = request.GET.get('q', '')
    if q:
        salaries = salaries.filter(
            Q(employee__first_name__icontains=q) | Q(employee__last_name__icontains=q)
        )
    paginator = Paginator(salaries, ITEMS)
    salaries = paginator.get_page(request.GET.get('page'))
    return render(request, 'hr/salary_list.html', {'salaries': salaries, 'query': q})


@login_required
@hr_required
def salary_create(request):
    """Create/update salary structure."""
    form = SalaryStructureForm()
    if request.method == 'POST':
        form = SalaryStructureForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salary structure saved.')
            return redirect('hr:salary_list')
    return render(request, 'hr/generic_form.html', {
        'form': form, 'title': 'Add Salary Structure', 'button_text': 'Save',
    })


@login_required
@hr_required
def salary_edit(request, pk):
    """Edit salary structure."""
    salary = get_object_or_404(SalaryStructure, pk=pk)
    form = SalaryStructureForm(instance=salary)
    if request.method == 'POST':
        form = SalaryStructureForm(request.POST, instance=salary)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salary structure updated.')
            return redirect('hr:salary_list')
    return render(request, 'hr/generic_form.html', {
        'form': form, 'title': 'Edit Salary Structure', 'button_text': 'Update',
    })


@login_required
@hr_required
def salary_detail(request, pk):
    """Salary structure detail view."""
    salary = get_object_or_404(SalaryStructure, pk=pk)
    return render(request, 'hr/salary_detail.html', {'salary': salary})


# ===========================================================================
# RECRUITMENT - JOB OPENINGS
# ===========================================================================

@login_required
@hr_required
def job_opening_list(request):
    """List job openings."""
    openings = JobOpening.objects.select_related('department').all()
    status_filter = request.GET.get('status', '')
    if status_filter:
        openings = openings.filter(status=status_filter)
    q = request.GET.get('q', '')
    if q:
        openings = openings.filter(Q(title__icontains=q) | Q(department__name__icontains=q))
    paginator = Paginator(openings, ITEMS)
    openings = paginator.get_page(request.GET.get('page'))
    return render(request, 'hr/job_opening_list.html', {
        'openings': openings, 'status_filter': status_filter, 'query': q,
    })


@login_required
@hr_required
def job_opening_create(request):
    form = JobOpeningForm()
    if request.method == 'POST':
        form = JobOpeningForm(request.POST)
        if form.is_valid():
            opening = form.save(commit=False)
            opening.posted_by = request.user
            opening.save()
            messages.success(request, 'Job opening created.')
            return redirect('hr:job_opening_list')
    return render(request, 'hr/generic_form.html', {
        'form': form, 'title': 'Create Job Opening', 'button_text': 'Create',
    })


@login_required
@hr_required
def job_opening_edit(request, pk):
    opening = get_object_or_404(JobOpening, pk=pk)
    form = JobOpeningForm(instance=opening)
    if request.method == 'POST':
        form = JobOpeningForm(request.POST, instance=opening)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job opening updated.')
            return redirect('hr:job_opening_list')
    return render(request, 'hr/generic_form.html', {
        'form': form, 'title': f'Edit: {opening.title}', 'button_text': 'Update',
    })


@login_required
@hr_required
def job_opening_detail(request, pk):
    opening = get_object_or_404(JobOpening, pk=pk)
    candidates = opening.candidates.all()
    return render(request, 'hr/job_opening_detail.html', {
        'opening': opening, 'candidates': candidates,
    })


# ===========================================================================
# RECRUITMENT - CANDIDATES
# ===========================================================================

@login_required
@hr_required
def candidate_list(request):
    candidates = Candidate.objects.select_related('job_opening').all()
    status_filter = request.GET.get('status', '')
    if status_filter:
        candidates = candidates.filter(status=status_filter)
    q = request.GET.get('q', '')
    if q:
        candidates = candidates.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q)
        )
    paginator = Paginator(candidates, ITEMS)
    candidates = paginator.get_page(request.GET.get('page'))
    return render(request, 'hr/candidate_list.html', {
        'candidates': candidates, 'status_filter': status_filter, 'query': q,
    })


@login_required
@hr_required
def candidate_create(request):
    form = CandidateForm()
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidate added.')
            return redirect('hr:candidate_list')
    return render(request, 'hr/generic_form.html', {
        'form': form, 'title': 'Add Candidate', 'button_text': 'Save',
    })


@login_required
@hr_required
def candidate_edit(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    form = CandidateForm(instance=candidate)
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidate updated.')
            return redirect('hr:candidate_list')
    return render(request, 'hr/generic_form.html', {
        'form': form, 'title': f'Edit: {candidate.first_name} {candidate.last_name}',
        'button_text': 'Update',
    })


@login_required
@hr_required
def candidate_detail(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    interviews = candidate.interviews.all()
    return render(request, 'hr/candidate_detail.html', {
        'candidate': candidate, 'interviews': interviews,
    })


# ===========================================================================
# RECRUITMENT - INTERVIEWS
# ===========================================================================

@login_required
@hr_required
def interview_create(request):
    form = InterviewForm()
    if request.method == 'POST':
        form = InterviewForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Interview scheduled.')
            return redirect('hr:candidate_list')
    return render(request, 'hr/generic_form.html', {
        'form': form, 'title': 'Schedule Interview', 'button_text': 'Schedule',
    })


@login_required
@hr_required
def interview_edit(request, pk):
    interview = get_object_or_404(Interview, pk=pk)
    form = InterviewForm(instance=interview)
    if request.method == 'POST':
        form = InterviewForm(request.POST, instance=interview)
        if form.is_valid():
            form.save()
            messages.success(request, 'Interview updated.')
            return redirect('hr:candidate_detail', pk=interview.candidate.pk)
    return render(request, 'hr/generic_form.html', {
        'form': form, 'title': f'Edit Interview: {interview.round_name}',
        'button_text': 'Update',
    })


# ===========================================================================
# PERFORMANCE (APPRAISAL)
# ===========================================================================

@login_required
@hr_required
def appraisal_list(request):
    appraisals = Appraisal.objects.select_related('employee', 'reviewer').all()
    q = request.GET.get('q', '')
    if q:
        appraisals = appraisals.filter(
            Q(employee__first_name__icontains=q) | Q(review_period__icontains=q)
        )
    paginator = Paginator(appraisals, ITEMS)
    appraisals = paginator.get_page(request.GET.get('page'))
    return render(request, 'hr/appraisal_list.html', {'appraisals': appraisals, 'query': q})


@login_required
@hr_required
def appraisal_create(request):
    form = AppraisalForm()
    if request.method == 'POST':
        form = AppraisalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appraisal record created.')
            return redirect('hr:appraisal_list')
    return render(request, 'hr/generic_form.html', {
        'form': form, 'title': 'Create Appraisal', 'button_text': 'Create',
    })


@login_required
@hr_required
def appraisal_edit(request, pk):
    appraisal = get_object_or_404(Appraisal, pk=pk)
    form = AppraisalForm(instance=appraisal)
    if request.method == 'POST':
        form = AppraisalForm(request.POST, instance=appraisal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appraisal updated.')
            return redirect('hr:appraisal_list')
    return render(request, 'hr/generic_form.html', {
        'form': form, 'title': 'Edit Appraisal', 'button_text': 'Update',
    })


@login_required
@hr_required
def appraisal_detail(request, pk):
    appraisal = get_object_or_404(Appraisal, pk=pk)
    return render(request, 'hr/appraisal_detail.html', {'appraisal': appraisal})


# ===========================================================================
# TRAINING
# ===========================================================================

@login_required
@hr_required
def training_list(request):
    trainings = TrainingSession.objects.select_related('department').all()
    status_filter = request.GET.get('status', '')
    if status_filter:
        trainings = trainings.filter(status=status_filter)
    paginator = Paginator(trainings, ITEMS)
    trainings = paginator.get_page(request.GET.get('page'))
    return render(request, 'hr/training_list.html', {
        'trainings': trainings, 'status_filter': status_filter,
    })


@login_required
@hr_required
def training_create(request):
    form = TrainingSessionForm()
    if request.method == 'POST':
        form = TrainingSessionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Training session created.')
            return redirect('hr:training_list')
    return render(request, 'hr/generic_form.html', {
        'form': form, 'title': 'Create Training Session', 'button_text': 'Create',
    })


@login_required
@hr_required
def training_edit(request, pk):
    training = get_object_or_404(TrainingSession, pk=pk)
    form = TrainingSessionForm(instance=training)
    if request.method == 'POST':
        form = TrainingSessionForm(request.POST, instance=training)
        if form.is_valid():
            form.save()
            messages.success(request, 'Training session updated.')
            return redirect('hr:training_list')
    return render(request, 'hr/generic_form.html', {
        'form': form, 'title': f'Edit: {training.title}', 'button_text': 'Update',
    })


@login_required
@hr_required
def training_detail(request, pk):
    training = get_object_or_404(TrainingSession, pk=pk)
    assignments = training.assignments.select_related('employee').all()
    return render(request, 'hr/training_detail.html', {
        'training': training, 'assignments': assignments,
    })


@login_required
@hr_required
def training_assign(request):
    form = TrainingAssignmentForm()
    if request.method == 'POST':
        form = TrainingAssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee assigned to training.')
            return redirect('hr:training_list')
    return render(request, 'hr/generic_form.html', {
        'form': form, 'title': 'Assign Training', 'button_text': 'Assign',
    })


# ===========================================================================
# GRIEVANCE
# ===========================================================================

@login_required
@hr_required
def grievance_list(request):
    grievances = Grievance.objects.select_related('employee', 'assigned_to').all()
    status_filter = request.GET.get('status', '')
    if status_filter:
        grievances = grievances.filter(status=status_filter)
    paginator = Paginator(grievances, ITEMS)
    grievances = grievances[:ITEMS]  # Simple slice for now
    return render(request, 'hr/grievance_list.html', {
        'grievances': grievances, 'status_filter': status_filter,
    })


@login_required
@hr_required
def grievance_create(request):
    form = GrievanceForm()
    if request.method == 'POST':
        form = GrievanceForm(request.POST)
        if form.is_valid():
            grievance = form.save(commit=False)
            grievance.employee = request.user
            grievance.save()
            messages.success(request, 'Grievance submitted.')
            return redirect('hr:grievance_list')
    return render(request, 'hr/generic_form.html', {
        'form': form, 'title': 'Submit Grievance', 'button_text': 'Submit',
    })


@login_required
@hr_required
def grievance_detail(request, pk):
    grievance = get_object_or_404(Grievance, pk=pk)
    update_form = GrievanceUpdateForm(instance=grievance)
    if request.method == 'POST':
        update_form = GrievanceUpdateForm(request.POST, instance=grievance)
        if update_form.is_valid():
            g = update_form.save()
            if g.status == 'resolved':
                g.resolved_date = timezone.now()
                g.save()
            messages.success(request, 'Grievance updated.')
            return redirect('hr:grievance_list')
    return render(request, 'hr/grievance_detail.html', {
        'grievance': grievance, 'update_form': update_form,
    })


# ===========================================================================
# EXIT MANAGEMENT
# ===========================================================================

@login_required
@hr_required
def exit_list(request):
    exits = ExitRecord.objects.select_related('employee').all()
    status_filter = request.GET.get('status', '')
    if status_filter:
        exits = exits.filter(status=status_filter)
    paginator = Paginator(exits, ITEMS)
    exits = paginator.get_page(request.GET.get('page'))
    return render(request, 'hr/exit_list.html', {
        'exits': exits, 'status_filter': status_filter,
    })


@login_required
@hr_required
def exit_create(request):
    form = ExitRecordForm()
    if request.method == 'POST':
        form = ExitRecordForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exit record created.')
            return redirect('hr:exit_list')
    return render(request, 'hr/generic_form.html', {
        'form': form, 'title': 'Create Exit Record', 'button_text': 'Create',
    })


@login_required
@hr_required
def exit_edit(request, pk):
    record = get_object_or_404(ExitRecord, pk=pk)
    form = ExitRecordForm(instance=record)
    if request.method == 'POST':
        form = ExitRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exit record updated.')
            return redirect('hr:exit_list')
    return render(request, 'hr/generic_form.html', {
        'form': form, 'title': 'Edit Exit Record', 'button_text': 'Update',
    })


@login_required
@hr_required
def exit_detail(request, pk):
    record = get_object_or_404(ExitRecord, pk=pk)
    action_form = None
    
    # Only show action form if it's pending or in notice period
    if record.status in ['initiated', 'notice_period', 'exit_interview']:
        action_form = ExitActionForm()

    if request.method == 'POST' and action_form:
        action_form = ExitActionForm(request.POST)
        if action_form.is_valid():
            action = action_form.cleaned_data['action']
            remarks = action_form.cleaned_data.get('remarks', '')
            notice_days = action_form.cleaned_data.get('notice_period_days') or 0
            
            try:
                if action == 'notice_period' and record.status == 'initiated':
                    WorkflowService.approve_resignation(record, request.user, notice_days, remarks)
                    messages.success(request, 'Resignation approved. Notice period started.')
                    EmailNotificationService.send_and_create_notification(
                        user=record.employee, title="Resignation Approved",
                        message=f"Your resignation was approved. Your notice period ends on {record.last_working_day}.",
                        level="warning", link=f"/portal/resignation/"
                    )
                elif action == 'completed' and record.status in ['notice_period', 'exit_interview']:
                    WorkflowService.mark_exit_completed(record, request.user, remarks)
                    messages.success(request, 'Final clearance completed. User deactivated.')
                elif action == 'rejected' and record.status == 'initiated':
                    record.status = 'withdrawn' # Using withdrawn/rejected synonym
                    record.comments += f"\nHR Rejected: {remarks}"
                    record.save()
                    WorkflowService.add_action(record, 'rejected', request.user, remarks)
                    messages.error(request, 'Resignation rejected.')
            except ValueError as e:
                messages.error(request, str(e))
                
            return redirect('hr:exit_list')

    return render(request, 'hr/exit_detail.html', {'record': record, 'action_form': action_form})
