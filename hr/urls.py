"""
HR URL Configuration
"""
from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    # Employee Directory
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),

    # Attendance
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/mark/', views.attendance_create, name='attendance_create'),
    path('attendance/<int:pk>/edit/', views.attendance_edit, name='attendance_edit'),

    # Leave Management
    path('leaves/', views.leave_list, name='leave_list'),
    path('leaves/apply/', views.leave_create, name='leave_create'),
    path('leaves/<int:pk>/', views.leave_detail, name='leave_detail'),

    # Payroll
    path('payroll/', views.salary_list, name='salary_list'),
    path('payroll/create/', views.salary_create, name='salary_create'),
    path('payroll/<int:pk>/', views.salary_detail, name='salary_detail'),
    path('payroll/<int:pk>/edit/', views.salary_edit, name='salary_edit'),

    # Recruitment - Job Openings
    path('jobs/', views.job_opening_list, name='job_opening_list'),
    path('jobs/create/', views.job_opening_create, name='job_opening_create'),
    path('jobs/<int:pk>/', views.job_opening_detail, name='job_opening_detail'),
    path('jobs/<int:pk>/edit/', views.job_opening_edit, name='job_opening_edit'),

    # Recruitment - Candidates
    path('candidates/', views.candidate_list, name='candidate_list'),
    path('candidates/add/', views.candidate_create, name='candidate_create'),
    path('candidates/<int:pk>/', views.candidate_detail, name='candidate_detail'),
    path('candidates/<int:pk>/edit/', views.candidate_edit, name='candidate_edit'),

    # Interviews
    path('interviews/schedule/', views.interview_create, name='interview_create'),
    path('interviews/<int:pk>/edit/', views.interview_edit, name='interview_edit'),

    # Performance (Appraisal)
    path('appraisals/', views.appraisal_list, name='appraisal_list'),
    path('appraisals/create/', views.appraisal_create, name='appraisal_create'),
    path('appraisals/<int:pk>/', views.appraisal_detail, name='appraisal_detail'),
    path('appraisals/<int:pk>/edit/', views.appraisal_edit, name='appraisal_edit'),

    # Training
    path('training/', views.training_list, name='training_list'),
    path('training/create/', views.training_create, name='training_create'),
    path('training/<int:pk>/', views.training_detail, name='training_detail'),
    path('training/<int:pk>/edit/', views.training_edit, name='training_edit'),
    path('training/assign/', views.training_assign, name='training_assign'),

    # Grievance
    path('grievances/', views.grievance_list, name='grievance_list'),
    path('grievances/submit/', views.grievance_create, name='grievance_create'),
    path('grievances/<int:pk>/', views.grievance_detail, name='grievance_detail'),

    # Exit Management
    path('exits/', views.exit_list, name='exit_list'),
    path('exits/create/', views.exit_create, name='exit_create'),
    path('exits/<int:pk>/', views.exit_detail, name='exit_detail'),
    path('exits/<int:pk>/edit/', views.exit_edit, name='exit_edit'),
]
