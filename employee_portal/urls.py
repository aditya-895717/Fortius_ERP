from django.urls import path
from . import views

app_name = 'employee_portal'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    
    # Leave
    path('leaves/', views.leave_list, name='leave_list'),
    path('leaves/apply/', views.leave_apply, name='leave_apply'),
    
    # Grievance
    path('grievances/', views.grievance_list, name='grievance_list'),
    path('grievances/submit/', views.grievance_submit, name='grievance_submit'),
    
    # Resignation
    path('resignation/', views.resignation_view, name='resignation_view'),
    path('resignation/submit/', views.resignation_submit, name='resignation_submit'),
]
