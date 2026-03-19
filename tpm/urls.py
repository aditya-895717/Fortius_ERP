"""
TPM URL Configuration
"""
from django.urls import path
from . import views

app_name = 'tpm'

urlpatterns = [
    # Projects
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),

    # Tasks
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/edit/', views.task_edit, name='task_edit'),

    # Milestones
    path('milestones/', views.milestone_list, name='milestone_list'),
    path('milestones/create/', views.milestone_create, name='milestone_create'),
    path('milestones/<int:pk>/edit/', views.milestone_edit, name='milestone_edit'),

    # Risks
    path('risks/', views.risk_list, name='risk_list'),
    path('risks/create/', views.risk_create, name='risk_create'),
    path('risks/<int:pk>/', views.risk_detail, name='risk_detail'),
    path('risks/<int:pk>/edit/', views.risk_edit, name='risk_edit'),

    # Issues
    path('issues/', views.issue_list, name='issue_list'),
    path('issues/create/', views.issue_create, name='issue_create'),
    path('issues/<int:pk>/', views.issue_detail, name='issue_detail'),
    path('issues/<int:pk>/edit/', views.issue_edit, name='issue_edit'),

    # Meetings
    path('meetings/', views.meeting_list, name='meeting_list'),
    path('meetings/create/', views.meeting_create, name='meeting_create'),
    path('meetings/<int:pk>/', views.meeting_detail, name='meeting_detail'),

    # Notes
    path('notes/', views.note_list, name='note_list'),
    path('notes/create/', views.note_create, name='note_create'),
    path('notes/<int:pk>/edit/', views.note_edit, name='note_edit'),
]
