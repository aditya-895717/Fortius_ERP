"""
Accounts URL Configuration
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('profile/', views.profile_view, name='profile'),

    # Admin: User Management
    path('users/', views.user_list_view, name='user_list'),
    path('users/create/', views.user_create_view, name='user_create'),
    path('users/<int:pk>/', views.user_detail_view, name='user_detail'),
    path('users/<int:pk>/edit/', views.user_edit_view, name='user_edit'),

    # Admin: Department Management
    path('departments/', views.department_list_view, name='department_list'),
    path('departments/create/', views.department_create_view, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit_view, name='department_edit'),
]
