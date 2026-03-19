"""
TPM Forms
=========
ModelForms for all TPM CRUD operations with Bootstrap styling.
"""
from django import forms
from django.contrib.auth.models import User
from .models import Project, Task, Milestone, Risk, Issue, Meeting, MeetingActionItem, ProjectNote

_ctrl = {'class': 'form-control'}
_select = {'class': 'form-select'}
_textarea = {'class': 'form-control', 'rows': 3}
_date = {'class': 'form-control', 'type': 'date'}
_datetime = {'class': 'form-control', 'type': 'datetime-local'}


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_code', 'name', 'description', 'client_name', 'department',
                  'manager', 'start_date', 'end_date', 'budget', 'status', 'priority',
                  'completion_percentage']
        widgets = {
            'project_code': forms.TextInput(attrs=_ctrl),
            'name': forms.TextInput(attrs=_ctrl),
            'description': forms.Textarea(attrs=_textarea),
            'client_name': forms.TextInput(attrs=_ctrl),
            'department': forms.Select(attrs=_select),
            'manager': forms.Select(attrs=_select),
            'start_date': forms.DateInput(attrs=_date),
            'end_date': forms.DateInput(attrs=_date),
            'budget': forms.NumberInput(attrs=_ctrl),
            'status': forms.Select(attrs=_select),
            'priority': forms.Select(attrs=_select),
            'completion_percentage': forms.NumberInput(attrs={**_ctrl, 'min': 0, 'max': 100}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['manager'].queryset = User.objects.filter(is_active=True).order_by('first_name')


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['project', 'title', 'description', 'assigned_to', 'priority',
                  'status', 'start_date', 'due_date', 'dependency',
                  'estimated_hours', 'actual_hours']
        widgets = {
            'project': forms.Select(attrs=_select),
            'title': forms.TextInput(attrs=_ctrl),
            'description': forms.Textarea(attrs=_textarea),
            'assigned_to': forms.Select(attrs=_select),
            'priority': forms.Select(attrs=_select),
            'status': forms.Select(attrs=_select),
            'start_date': forms.DateInput(attrs=_date),
            'due_date': forms.DateInput(attrs=_date),
            'dependency': forms.Select(attrs=_select),
            'estimated_hours': forms.NumberInput(attrs=_ctrl),
            'actual_hours': forms.NumberInput(attrs=_ctrl),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True).order_by('first_name')
        self.fields['dependency'].queryset = Task.objects.all()
        self.fields['dependency'].required = False


class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['project', 'title', 'description', 'due_date',
                  'completion_percentage', 'is_completed']
        widgets = {
            'project': forms.Select(attrs=_select),
            'title': forms.TextInput(attrs=_ctrl),
            'description': forms.Textarea(attrs=_textarea),
            'due_date': forms.DateInput(attrs=_date),
            'completion_percentage': forms.NumberInput(attrs={**_ctrl, 'min': 0, 'max': 100}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RiskForm(forms.ModelForm):
    class Meta:
        model = Risk
        fields = ['project', 'title', 'description', 'severity', 'impact',
                  'mitigation_plan', 'owner', 'status']
        widgets = {
            'project': forms.Select(attrs=_select),
            'title': forms.TextInput(attrs=_ctrl),
            'description': forms.Textarea(attrs=_textarea),
            'severity': forms.Select(attrs=_select),
            'impact': forms.Textarea(attrs=_textarea),
            'mitigation_plan': forms.Textarea(attrs=_textarea),
            'owner': forms.Select(attrs=_select),
            'status': forms.Select(attrs=_select),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['owner'].queryset = User.objects.filter(is_active=True)


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['project', 'title', 'description', 'category', 'criticality',
                  'status', 'assigned_to', 'resolution']
        widgets = {
            'project': forms.Select(attrs=_select),
            'title': forms.TextInput(attrs=_ctrl),
            'description': forms.Textarea(attrs=_textarea),
            'category': forms.Select(attrs=_select),
            'criticality': forms.Select(attrs=_select),
            'status': forms.Select(attrs=_select),
            'assigned_to': forms.Select(attrs=_select),
            'resolution': forms.Textarea(attrs=_textarea),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['project', 'title', 'meeting_date', 'location',
                  'discussion_points', 'decisions']
        widgets = {
            'project': forms.Select(attrs=_select),
            'title': forms.TextInput(attrs=_ctrl),
            'meeting_date': forms.DateTimeInput(attrs=_datetime),
            'location': forms.TextInput(attrs=_ctrl),
            'discussion_points': forms.Textarea(attrs=_textarea),
            'decisions': forms.Textarea(attrs=_textarea),
        }


class MeetingActionItemForm(forms.ModelForm):
    class Meta:
        model = MeetingActionItem
        fields = ['description', 'assigned_to', 'due_date', 'status']
        widgets = {
            'description': forms.Textarea(attrs={**_textarea, 'rows': 2}),
            'assigned_to': forms.Select(attrs=_select),
            'due_date': forms.DateInput(attrs=_date),
            'status': forms.Select(attrs=_select),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)


class ProjectNoteForm(forms.ModelForm):
    class Meta:
        model = ProjectNote
        fields = ['project', 'title', 'content', 'is_pinned']
        widgets = {
            'project': forms.Select(attrs=_select),
            'title': forms.TextInput(attrs=_ctrl),
            'content': forms.Textarea(attrs={**_textarea, 'rows': 5}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
