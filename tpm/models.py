"""
TPM Models
==========
Complete data models for Technical Project Management including:
Projects, Tasks, Milestones, Risks, Issues, Meetings, and Notes.
"""
from django.db import models
from django.contrib.auth.models import User
from accounts.models import Department


class Project(models.Model):
    """Project record with metadata, budget, and status tracking."""
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    project_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    client_name = models.CharField(max_length=200, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_projects')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='planning')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    completion_percentage = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.project_code} - {self.name}"


class Task(models.Model):
    """Task within a project."""
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('done', 'Done'),
        ('blocked', 'Blocked'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks'
    )
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='todo')
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    dependency = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='dependent_tasks',
        help_text='Task that must be completed before this one'
    )
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'due_date']

    def __str__(self):
        return f"{self.title} ({self.project.project_code})"

    @property
    def is_overdue(self):
        from django.utils import timezone
        if self.due_date and self.status not in ('done',):
            return self.due_date < timezone.now().date()
        return False


class Milestone(models.Model):
    """Project milestone with target date and completion tracking."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    completion_percentage = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.title} - {self.project.name}"


class Risk(models.Model):
    """Project risk assessment and mitigation record."""
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('identified', 'Identified'),
        ('mitigating', 'Mitigating'),
        ('resolved', 'Resolved'),
        ('accepted', 'Accepted'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='risks')
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    impact = models.TextField(blank=True)
    mitigation_plan = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='identified')
    identified_date = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-severity', '-identified_date']

    def __str__(self):
        return f"{self.title} ({self.project.project_code})"


class Issue(models.Model):
    """Project issue tracker."""
    CATEGORY_CHOICES = [
        ('bug', 'Bug'),
        ('feature', 'Feature Request'),
        ('technical', 'Technical Debt'),
        ('process', 'Process'),
        ('resource', 'Resource'),
        ('other', 'Other'),
    ]
    CRITICALITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='issues')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='bug')
    criticality = models.CharField(max_length=10, choices=CRITICALITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resolution = models.TextField(blank=True)
    reported_date = models.DateTimeField(auto_now_add=True)
    resolved_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-reported_date']

    def __str__(self):
        return f"{self.title} ({self.project.project_code})"


class Meeting(models.Model):
    """Client or internal meeting record."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='meetings')
    title = models.CharField(max_length=200)
    meeting_date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    attendees = models.ManyToManyField(User, blank=True, related_name='meetings_attended')
    discussion_points = models.TextField(blank=True)
    decisions = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-meeting_date']

    def __str__(self):
        return f"{self.title} - {self.meeting_date.strftime('%Y-%m-%d')}"


class MeetingActionItem(models.Model):
    """Action items from a meeting."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='action_items')
    description = models.TextField()
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.description[:50]} - {self.meeting.title}"


class ProjectNote(models.Model):
    """Internal collaboration notes for a project."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.project.name}"
