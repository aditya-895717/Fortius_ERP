"""
HR Forms
========
ModelForms for all HR CRUD operations with Bootstrap styling.
"""
from django import forms
from django.contrib.auth.models import User
from .models import (
    Attendance, LeaveRequest, LeaveType, LeaveBalance,
    SalaryStructure, PayrollRecord, JobOpening, Candidate, Interview,
    Appraisal, TrainingSession, TrainingAssignment, Grievance, ExitRecord
)

# Reusable widget attrs
_ctrl = {'class': 'form-control'}
_ctrl_sm = {'class': 'form-control form-control-sm'}
_select = {'class': 'form-select'}
_textarea = {'class': 'form-control', 'rows': 3}
_date = {'class': 'form-control', 'type': 'date'}
_datetime = {'class': 'form-control', 'type': 'datetime-local'}
_time = {'class': 'form-control', 'type': 'time'}
_check = {'class': 'form-check-input'}
_file = {'class': 'form-control'}


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'status', 'check_in', 'check_out', 'remarks']
        widgets = {
            'employee': forms.Select(attrs=_select),
            'date': forms.DateInput(attrs=_date),
            'status': forms.Select(attrs=_select),
            'check_in': forms.TimeInput(attrs=_time),
            'check_out': forms.TimeInput(attrs=_time),
            'remarks': forms.TextInput(attrs=_ctrl),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = User.objects.filter(is_active=True).order_by('first_name')


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs=_select),
            'start_date': forms.DateInput(attrs=_date),
            'end_date': forms.DateInput(attrs=_date),
            'reason': forms.Textarea(attrs=_textarea),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        if start and end and end < start:
            raise forms.ValidationError('End date must be after start date.')
        return cleaned


class LeaveActionForm(forms.Form):
    """Form for approving/rejecting a leave request."""
    action = forms.ChoiceField(choices=[('approved', 'Approve'), ('rejected', 'Reject')],
                                widget=forms.Select(attrs=_select))
    rejection_reason = forms.CharField(required=False, widget=forms.Textarea(attrs=_textarea))

class ExitActionForm(forms.Form):
    """Form for HR to approve resignation and set notice period."""
    action = forms.ChoiceField(choices=[
        ('notice_period', 'Approve Resignation & Start Notice Period'),
        ('completed', 'Final Exit Clearance Completed'),
        ('rejected', 'Reject Resignation')
    ], widget=forms.Select(attrs=_select))
    notice_period_days = forms.IntegerField(required=False, initial=30, widget=forms.NumberInput(attrs=_ctrl))
    remarks = forms.CharField(required=False, widget=forms.Textarea(attrs=_textarea))



class SalaryStructureForm(forms.ModelForm):
    class Meta:
        model = SalaryStructure
        fields = ['employee', 'basic_salary', 'hra', 'transport_allowance',
                  'medical_allowance', 'special_allowance', 'pf_deduction',
                  'tax_deduction', 'other_deductions', 'effective_date']
        widgets = {
            'employee': forms.Select(attrs=_select),
            'basic_salary': forms.NumberInput(attrs=_ctrl),
            'hra': forms.NumberInput(attrs=_ctrl),
            'transport_allowance': forms.NumberInput(attrs=_ctrl),
            'medical_allowance': forms.NumberInput(attrs=_ctrl),
            'special_allowance': forms.NumberInput(attrs=_ctrl),
            'pf_deduction': forms.NumberInput(attrs=_ctrl),
            'tax_deduction': forms.NumberInput(attrs=_ctrl),
            'other_deductions': forms.NumberInput(attrs=_ctrl),
            'effective_date': forms.DateInput(attrs=_date),
        }


class JobOpeningForm(forms.ModelForm):
    class Meta:
        model = JobOpening
        fields = ['title', 'department', 'description', 'requirements', 'positions',
                  'location', 'salary_range', 'priority', 'status', 'closing_date']
        widgets = {
            'title': forms.TextInput(attrs=_ctrl),
            'department': forms.Select(attrs=_select),
            'description': forms.Textarea(attrs=_textarea),
            'requirements': forms.Textarea(attrs=_textarea),
            'positions': forms.NumberInput(attrs=_ctrl),
            'location': forms.TextInput(attrs=_ctrl),
            'salary_range': forms.TextInput(attrs=_ctrl),
            'priority': forms.Select(attrs=_select),
            'status': forms.Select(attrs=_select),
            'closing_date': forms.DateInput(attrs=_date),
        }


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['job_opening', 'first_name', 'last_name', 'email', 'phone',
                  'resume', 'experience_years', 'current_company', 'expected_salary',
                  'status', 'notes']
        widgets = {
            'job_opening': forms.Select(attrs=_select),
            'first_name': forms.TextInput(attrs=_ctrl),
            'last_name': forms.TextInput(attrs=_ctrl),
            'email': forms.EmailInput(attrs=_ctrl),
            'phone': forms.TextInput(attrs=_ctrl),
            'resume': forms.FileInput(attrs=_file),
            'experience_years': forms.NumberInput(attrs=_ctrl),
            'current_company': forms.TextInput(attrs=_ctrl),
            'expected_salary': forms.NumberInput(attrs=_ctrl),
            'status': forms.Select(attrs=_select),
            'notes': forms.Textarea(attrs=_textarea),
        }


class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['candidate', 'round_name', 'interviewer', 'scheduled_date',
                  'location', 'status', 'result', 'feedback']
        widgets = {
            'candidate': forms.Select(attrs=_select),
            'round_name': forms.TextInput(attrs=_ctrl),
            'interviewer': forms.Select(attrs=_select),
            'scheduled_date': forms.DateTimeInput(attrs=_datetime),
            'location': forms.TextInput(attrs=_ctrl),
            'status': forms.Select(attrs=_select),
            'result': forms.Select(attrs=_select),
            'feedback': forms.Textarea(attrs=_textarea),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['interviewer'].queryset = User.objects.filter(is_active=True).order_by('first_name')


class AppraisalForm(forms.ModelForm):
    class Meta:
        model = Appraisal
        fields = ['employee', 'review_period', 'reviewer', 'rating',
                  'goals_achieved', 'areas_of_improvement', 'comments', 'status']
        widgets = {
            'employee': forms.Select(attrs=_select),
            'review_period': forms.TextInput(attrs=_ctrl),
            'reviewer': forms.Select(attrs=_select),
            'rating': forms.Select(attrs=_select),
            'goals_achieved': forms.Textarea(attrs=_textarea),
            'areas_of_improvement': forms.Textarea(attrs=_textarea),
            'comments': forms.Textarea(attrs=_textarea),
            'status': forms.Select(attrs=_select),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = User.objects.filter(is_active=True)
        self.fields['reviewer'].queryset = User.objects.filter(is_active=True)


class TrainingSessionForm(forms.ModelForm):
    class Meta:
        model = TrainingSession
        fields = ['title', 'description', 'trainer', 'department', 'start_date',
                  'end_date', 'location', 'max_participants', 'status']
        widgets = {
            'title': forms.TextInput(attrs=_ctrl),
            'description': forms.Textarea(attrs=_textarea),
            'trainer': forms.TextInput(attrs=_ctrl),
            'department': forms.Select(attrs=_select),
            'start_date': forms.DateInput(attrs=_date),
            'end_date': forms.DateInput(attrs=_date),
            'location': forms.TextInput(attrs=_ctrl),
            'max_participants': forms.NumberInput(attrs=_ctrl),
            'status': forms.Select(attrs=_select),
        }


class TrainingAssignmentForm(forms.ModelForm):
    class Meta:
        model = TrainingAssignment
        fields = ['training', 'employee', 'status', 'completion_date', 'score', 'feedback']
        widgets = {
            'training': forms.Select(attrs=_select),
            'employee': forms.Select(attrs=_select),
            'status': forms.Select(attrs=_select),
            'completion_date': forms.DateInput(attrs=_date),
            'score': forms.NumberInput(attrs=_ctrl),
            'feedback': forms.Textarea(attrs=_textarea),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = User.objects.filter(is_active=True)


class GrievanceForm(forms.ModelForm):
    class Meta:
        model = Grievance
        fields = ['category', 'subject', 'description']
        widgets = {
            'category': forms.Select(attrs=_select),
            'subject': forms.TextInput(attrs=_ctrl),
            'description': forms.Textarea(attrs=_textarea),
        }


class GrievanceUpdateForm(forms.ModelForm):
    class Meta:
        model = Grievance
        fields = ['status', 'assigned_to', 'resolution']
        widgets = {
            'status': forms.Select(attrs=_select),
            'assigned_to': forms.Select(attrs=_select),
            'resolution': forms.Textarea(attrs=_textarea),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)


class ExitRecordForm(forms.ModelForm):
    class Meta:
        model = ExitRecord
        fields = ['employee', 'reason', 'resignation_date', 'last_working_day',
                  'notice_period_days', 'exit_interview_date', 'exit_interview_notes',
                  'status', 'full_final_status', 'comments']
        widgets = {
            'employee': forms.Select(attrs=_select),
            'reason': forms.Select(attrs=_select),
            'resignation_date': forms.DateInput(attrs=_date),
            'last_working_day': forms.DateInput(attrs=_date),
            'notice_period_days': forms.NumberInput(attrs=_ctrl),
            'exit_interview_date': forms.DateInput(attrs=_date),
            'exit_interview_notes': forms.Textarea(attrs=_textarea),
            'status': forms.Select(attrs=_select),
            'full_final_status': forms.TextInput(attrs=_ctrl),
            'comments': forms.Textarea(attrs=_textarea),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = User.objects.filter(is_active=True)
