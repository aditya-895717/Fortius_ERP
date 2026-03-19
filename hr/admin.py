"""
HR Admin
"""
from django.contrib import admin
from .models import (
    Attendance, LeaveType, LeaveRequest, LeaveBalance,
    SalaryStructure, PayrollRecord, JobOpening, Candidate, Interview,
    Appraisal, TrainingSession, TrainingAssignment, Grievance, ExitRecord
)

admin.site.register(Attendance)
admin.site.register(LeaveType)
admin.site.register(LeaveRequest)
admin.site.register(LeaveBalance)
admin.site.register(SalaryStructure)
admin.site.register(PayrollRecord)
admin.site.register(JobOpening)
admin.site.register(Candidate)
admin.site.register(Interview)
admin.site.register(Appraisal)
admin.site.register(TrainingSession)
admin.site.register(TrainingAssignment)
admin.site.register(Grievance)
admin.site.register(ExitRecord)
