from django import forms
from hr.models import LeaveRequest, Grievance, ExitRecord

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
        }

class GrievanceForm(forms.ModelForm):
    class Meta:
        model = Grievance
        fields = ['category', 'subject', 'description']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

class ResignationForm(forms.ModelForm):
    class Meta:
        model = ExitRecord
        fields = ['resignation_date', 'reason', 'comments']
        widgets = {
            'resignation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'comments': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Optional comments regarding your resignation...'}),
        }
