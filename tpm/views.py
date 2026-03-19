"""
TPM Views
=========
Complete CRUD views for all TPM modules with role-based access control.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q, Count

from accounts.decorators import tpm_required
from core.models import ActivityLog
from .models import Project, Task, Milestone, Risk, Issue, Meeting, MeetingActionItem, ProjectNote
from .forms import (
    ProjectForm, TaskForm, MilestoneForm, RiskForm, IssueForm,
    MeetingForm, MeetingActionItemForm, ProjectNoteForm
)

ITEMS = 15


# ===========================================================================
# PROJECTS
# ===========================================================================

@login_required
@tpm_required
def project_list(request):
    """List all projects with search and filters."""
    projects = Project.objects.select_related('department', 'manager').all()

    q = request.GET.get('q', '')
    if q:
        projects = projects.filter(
            Q(name__icontains=q) | Q(project_code__icontains=q) | Q(client_name__icontains=q)
        )

    status_filter = request.GET.get('status', '')
    if status_filter:
        projects = projects.filter(status=status_filter)

    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        projects = projects.filter(priority=priority_filter)

    paginator = Paginator(projects, ITEMS)
    projects = paginator.get_page(request.GET.get('page'))

    return render(request, 'tpm/project_list.html', {
        'projects': projects, 'query': q,
        'status_filter': status_filter, 'priority_filter': priority_filter,
    })


@login_required
@tpm_required
def project_create(request):
    form = ProjectForm()
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            ActivityLog.objects.create(
                user=request.user, action='create',
                model_name='Project', object_id=project.id,
                object_repr=str(project), details=f'Created project {project.name}'
            )
            messages.success(request, f'Project "{project.name}" created.')
            return redirect('tpm:project_list')
    return render(request, 'tpm/generic_form.html', {
        'form': form, 'title': 'Create Project', 'button_text': 'Create',
    })


@login_required
@tpm_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    form = ProjectForm(instance=project)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Project "{project.name}" updated.')
            return redirect('tpm:project_detail', pk=pk)
    return render(request, 'tpm/generic_form.html', {
        'form': form, 'title': f'Edit: {project.name}', 'button_text': 'Update',
    })


@login_required
@tpm_required
def project_detail(request, pk):
    """Project detail with tasks, milestones, risks, issues summary."""
    project = get_object_or_404(Project, pk=pk)
    tasks = project.tasks.all()[:10]
    milestones = project.milestones.all()[:5]
    risks = project.risks.filter(status__in=['identified', 'mitigating'])[:5]
    issues = project.issues.filter(status__in=['open', 'in_progress'])[:5]
    notes = project.notes.all()[:5]

    context = {
        'project': project,
        'tasks': tasks,
        'milestones': milestones,
        'risks': risks,
        'issues': issues,
        'notes': notes,
        'total_tasks': project.tasks.count(),
        'completed_tasks': project.tasks.filter(status='done').count(),
        'overdue_tasks': project.tasks.filter(
            due_date__lt=timezone.now().date(), status__in=['todo', 'in_progress']
        ).count(),
    }
    return render(request, 'tpm/project_detail.html', context)


# ===========================================================================
# TASKS
# ===========================================================================

@login_required
@tpm_required
def task_list(request):
    tasks = Task.objects.select_related('project', 'assigned_to').all()

    q = request.GET.get('q', '')
    if q:
        tasks = tasks.filter(Q(title__icontains=q) | Q(project__name__icontains=q))

    status_filter = request.GET.get('status', '')
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    project_filter = request.GET.get('project', '')
    if project_filter:
        tasks = tasks.filter(project_id=project_filter)

    paginator = Paginator(tasks, ITEMS)
    tasks = paginator.get_page(request.GET.get('page'))

    return render(request, 'tpm/task_list.html', {
        'tasks': tasks, 'query': q,
        'status_filter': status_filter, 'priority_filter': priority_filter,
        'project_filter': project_filter,
        'projects': Project.objects.all(),
    })


@login_required
@tpm_required
def task_create(request):
    form = TaskForm()
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task created.')
            return redirect('tpm:task_list')
    return render(request, 'tpm/generic_form.html', {
        'form': form, 'title': 'Create Task', 'button_text': 'Create',
    })


@login_required
@tpm_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    form = TaskForm(instance=task)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            t = form.save()
            if t.status == 'done' and not t.completed_date:
                t.completed_date = timezone.now().date()
                t.save()
            messages.success(request, 'Task updated.')
            return redirect('tpm:task_list')
    return render(request, 'tpm/generic_form.html', {
        'form': form, 'title': f'Edit: {task.title}', 'button_text': 'Update',
    })


@login_required
@tpm_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'tpm/task_detail.html', {'task': task})


# ===========================================================================
# MILESTONES
# ===========================================================================

@login_required
@tpm_required
def milestone_list(request):
    milestones = Milestone.objects.select_related('project').all()
    project_filter = request.GET.get('project', '')
    if project_filter:
        milestones = milestones.filter(project_id=project_filter)
    paginator = Paginator(milestones, ITEMS)
    milestones = paginator.get_page(request.GET.get('page'))
    return render(request, 'tpm/milestone_list.html', {
        'milestones': milestones, 'project_filter': project_filter,
        'projects': Project.objects.all(),
    })


@login_required
@tpm_required
def milestone_create(request):
    form = MilestoneForm()
    if request.method == 'POST':
        form = MilestoneForm(request.POST)
        if form.is_valid():
            ms = form.save()
            if ms.is_completed and not ms.completed_date:
                ms.completed_date = timezone.now().date()
                ms.save()
            messages.success(request, 'Milestone created.')
            return redirect('tpm:milestone_list')
    return render(request, 'tpm/generic_form.html', {
        'form': form, 'title': 'Add Milestone', 'button_text': 'Create',
    })


@login_required
@tpm_required
def milestone_edit(request, pk):
    ms = get_object_or_404(Milestone, pk=pk)
    form = MilestoneForm(instance=ms)
    if request.method == 'POST':
        form = MilestoneForm(request.POST, instance=ms)
        if form.is_valid():
            ms = form.save()
            if ms.is_completed and not ms.completed_date:
                ms.completed_date = timezone.now().date()
                ms.save()
            messages.success(request, 'Milestone updated.')
            return redirect('tpm:milestone_list')
    return render(request, 'tpm/generic_form.html', {
        'form': form, 'title': f'Edit: {ms.title}', 'button_text': 'Update',
    })


# ===========================================================================
# RISKS
# ===========================================================================

@login_required
@tpm_required
def risk_list(request):
    risks = Risk.objects.select_related('project', 'owner').all()
    severity_filter = request.GET.get('severity', '')
    if severity_filter:
        risks = risks.filter(severity=severity_filter)
    project_filter = request.GET.get('project', '')
    if project_filter:
        risks = risks.filter(project_id=project_filter)
    paginator = Paginator(risks, ITEMS)
    risks = paginator.get_page(request.GET.get('page'))
    return render(request, 'tpm/risk_list.html', {
        'risks': risks, 'severity_filter': severity_filter,
        'project_filter': project_filter, 'projects': Project.objects.all(),
    })


@login_required
@tpm_required
def risk_create(request):
    form = RiskForm()
    if request.method == 'POST':
        form = RiskForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Risk registered.')
            return redirect('tpm:risk_list')
    return render(request, 'tpm/generic_form.html', {
        'form': form, 'title': 'Add Risk', 'button_text': 'Register',
    })


@login_required
@tpm_required
def risk_edit(request, pk):
    risk = get_object_or_404(Risk, pk=pk)
    form = RiskForm(instance=risk)
    if request.method == 'POST':
        form = RiskForm(request.POST, instance=risk)
        if form.is_valid():
            form.save()
            messages.success(request, 'Risk updated.')
            return redirect('tpm:risk_list')
    return render(request, 'tpm/generic_form.html', {
        'form': form, 'title': f'Edit Risk: {risk.title}', 'button_text': 'Update',
    })


@login_required
@tpm_required
def risk_detail(request, pk):
    risk = get_object_or_404(Risk, pk=pk)
    return render(request, 'tpm/risk_detail.html', {'risk': risk})


# ===========================================================================
# ISSUES
# ===========================================================================

@login_required
@tpm_required
def issue_list(request):
    issues = Issue.objects.select_related('project', 'assigned_to').all()
    status_filter = request.GET.get('status', '')
    if status_filter:
        issues = issues.filter(status=status_filter)
    project_filter = request.GET.get('project', '')
    if project_filter:
        issues = issues.filter(project_id=project_filter)
    paginator = Paginator(issues, ITEMS)
    issues = paginator.get_page(request.GET.get('page'))
    return render(request, 'tpm/issue_list.html', {
        'issues': issues, 'status_filter': status_filter,
        'project_filter': project_filter, 'projects': Project.objects.all(),
    })


@login_required
@tpm_required
def issue_create(request):
    form = IssueForm()
    if request.method == 'POST':
        form = IssueForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Issue created.')
            return redirect('tpm:issue_list')
    return render(request, 'tpm/generic_form.html', {
        'form': form, 'title': 'Report Issue', 'button_text': 'Submit',
    })


@login_required
@tpm_required
def issue_edit(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    form = IssueForm(instance=issue)
    if request.method == 'POST':
        form = IssueForm(request.POST, instance=issue)
        if form.is_valid():
            form.save()
            messages.success(request, 'Issue updated.')
            return redirect('tpm:issue_list')
    return render(request, 'tpm/generic_form.html', {
        'form': form, 'title': f'Edit Issue: {issue.title}', 'button_text': 'Update',
    })


@login_required
@tpm_required
def issue_detail(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    return render(request, 'tpm/issue_detail.html', {'issue': issue})


# ===========================================================================
# MEETINGS
# ===========================================================================

@login_required
@tpm_required
def meeting_list(request):
    meetings = Meeting.objects.select_related('project', 'created_by').all()
    project_filter = request.GET.get('project', '')
    if project_filter:
        meetings = meetings.filter(project_id=project_filter)
    paginator = Paginator(meetings, ITEMS)
    meetings = paginator.get_page(request.GET.get('page'))
    return render(request, 'tpm/meeting_list.html', {
        'meetings': meetings, 'project_filter': project_filter,
        'projects': Project.objects.all(),
    })


@login_required
@tpm_required
def meeting_create(request):
    form = MeetingForm()
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.created_by = request.user
            meeting.save()
            messages.success(request, 'Meeting recorded.')
            return redirect('tpm:meeting_list')
    return render(request, 'tpm/generic_form.html', {
        'form': form, 'title': 'Create Meeting', 'button_text': 'Save',
    })


@login_required
@tpm_required
def meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    action_items = meeting.action_items.select_related('assigned_to').all()
    action_form = MeetingActionItemForm()

    if request.method == 'POST':
        action_form = MeetingActionItemForm(request.POST)
        if action_form.is_valid():
            ai = action_form.save(commit=False)
            ai.meeting = meeting
            ai.save()
            messages.success(request, 'Action item added.')
            return redirect('tpm:meeting_detail', pk=pk)

    return render(request, 'tpm/meeting_detail.html', {
        'meeting': meeting, 'action_items': action_items,
        'action_form': action_form,
    })


# ===========================================================================
# PROJECT NOTES
# ===========================================================================

@login_required
@tpm_required
def note_list(request):
    notes = ProjectNote.objects.select_related('project', 'author').all()
    project_filter = request.GET.get('project', '')
    if project_filter:
        notes = notes.filter(project_id=project_filter)
    paginator = Paginator(notes, ITEMS)
    notes = paginator.get_page(request.GET.get('page'))
    return render(request, 'tpm/note_list.html', {
        'notes': notes, 'project_filter': project_filter,
        'projects': Project.objects.all(),
    })


@login_required
@tpm_required
def note_create(request):
    form = ProjectNoteForm()
    if request.method == 'POST':
        form = ProjectNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.author = request.user
            note.save()
            messages.success(request, 'Note created.')
            return redirect('tpm:note_list')
    return render(request, 'tpm/generic_form.html', {
        'form': form, 'title': 'Add Note', 'button_text': 'Save',
    })


@login_required
@tpm_required
def note_edit(request, pk):
    note = get_object_or_404(ProjectNote, pk=pk)
    form = ProjectNoteForm(instance=note)
    if request.method == 'POST':
        form = ProjectNoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'Note updated.')
            return redirect('tpm:note_list')
    return render(request, 'tpm/generic_form.html', {
        'form': form, 'title': f'Edit Note', 'button_text': 'Update',
    })
