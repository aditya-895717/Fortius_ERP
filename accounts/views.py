"""
Accounts Views
==============
Authentication, user management, department management, and profile views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import UserProfile, Department, Role
from .forms import (
    LoginForm, UserProfileForm, AdminUserCreationForm,
    AdminUserEditForm, DepartmentForm
)
from .decorators import admin_required
from core.models import ActivityLog


# ---------------------------------------------------------------------------
# Authentication Views
# ---------------------------------------------------------------------------

def login_view(request):
    """Handle user login and redirect to role-based dashboard."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # Log activity
                    ActivityLog.objects.create(
                        user=user, action='login',
                        details=f'{user.username} logged in'
                    )
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    # Redirect to next or dashboard
                    next_url = request.GET.get('next', '')
                    return redirect(next_url if next_url else 'core:dashboard')
                else:
                    messages.error(request, 'Your account is inactive. Please contact admin.')
            else:
                messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Log out the user and redirect to login page."""
    ActivityLog.objects.create(
        user=request.user, action='logout',
        details=f'{request.user.username} logged out'
    )
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


@login_required
def change_password_view(request):
    """Allow user to change their password."""
    form = PasswordChangeForm(request.user)
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'accounts/change_password.html', {'form': form})


def forgot_password_view(request):
    """Forgot password placeholder page."""
    return render(request, 'accounts/forgot_password.html')


# ---------------------------------------------------------------------------
# Profile Views
# ---------------------------------------------------------------------------

@login_required
def profile_view(request):
    """View and edit own user profile."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    form = UserProfileForm(instance=profile)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save()
            # Update User model fields
            request.user.first_name = form.cleaned_data.get('first_name', request.user.first_name)
            request.user.last_name = form.cleaned_data.get('last_name', request.user.last_name)
            request.user.email = form.cleaned_data.get('email', request.user.email)
            request.user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')

    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile': profile,
    })


# ---------------------------------------------------------------------------
# Admin: User Management
# ---------------------------------------------------------------------------

@login_required
@admin_required
def user_list_view(request):
    """List all users with search and filter."""
    users = User.objects.select_related('profile', 'profile__role', 'profile__department').all()

    # Search
    query = request.GET.get('q', '')
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(profile__employee_id__icontains=query)
        )

    # Filter by role
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(profile__role__name=role_filter)

    # Filter by department
    dept_filter = request.GET.get('department', '')
    if dept_filter:
        users = users.filter(profile__department__id=dept_filter)

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        users = users.filter(profile__status=status_filter)

    paginator = Paginator(users, 15)
    page = request.GET.get('page')
    users = paginator.get_page(page)

    return render(request, 'accounts/user_list.html', {
        'users': users,
        'query': query,
        'role_filter': role_filter,
        'dept_filter': dept_filter,
        'status_filter': status_filter,
        'roles': Role.objects.filter(is_active=True),
        'departments': Department.objects.filter(is_active=True),
    })


@login_required
@admin_required
def user_create_view(request):
    """Admin creates a new user with profile."""
    form = AdminUserCreationForm()
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Create profile
            UserProfile.objects.create(
                user=user,
                role=form.cleaned_data.get('role'),
                department=form.cleaned_data.get('department'),
                employee_id=form.cleaned_data.get('employee_id'),
                designation=form.cleaned_data.get('designation'),
                phone=form.cleaned_data.get('phone'),
                date_of_joining=form.cleaned_data.get('date_of_joining'),
            )
            ActivityLog.objects.create(
                user=request.user, action='create',
                model_name='User', object_id=user.id,
                object_repr=str(user), details=f'Created user {user.username}'
            )
            messages.success(request, f'User {user.username} created successfully.')
            return redirect('accounts:user_list')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': 'Create New User',
        'button_text': 'Create User',
    })


@login_required
@admin_required
def user_edit_view(request, pk):
    """Admin edits an existing user."""
    user_obj = get_object_or_404(User, pk=pk)
    profile, created = UserProfile.objects.get_or_create(user=user_obj)

    initial_data = {
        'role': profile.role,
        'department': profile.department,
        'employee_id': profile.employee_id,
        'designation': profile.designation,
        'phone': profile.phone,
        'status': profile.status,
        'date_of_joining': profile.date_of_joining,
    }

    form = AdminUserEditForm(instance=user_obj, initial=initial_data)

    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            # Update profile
            profile.role = form.cleaned_data.get('role')
            profile.department = form.cleaned_data.get('department')
            profile.employee_id = form.cleaned_data.get('employee_id')
            profile.designation = form.cleaned_data.get('designation')
            profile.phone = form.cleaned_data.get('phone')
            profile.status = form.cleaned_data.get('status')
            profile.date_of_joining = form.cleaned_data.get('date_of_joining')
            profile.save()
            ActivityLog.objects.create(
                user=request.user, action='update',
                model_name='User', object_id=user_obj.id,
                object_repr=str(user_obj), details=f'Updated user {user_obj.username}'
            )
            messages.success(request, f'User {user_obj.username} updated successfully.')
            return redirect('accounts:user_list')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': f'Edit User: {user_obj.username}',
        'button_text': 'Save Changes',
        'edit_mode': True,
    })


@login_required
@admin_required
def user_detail_view(request, pk):
    """View user detail."""
    user_obj = get_object_or_404(User, pk=pk)
    profile = getattr(user_obj, 'profile', None)
    return render(request, 'accounts/user_detail.html', {
        'user_obj': user_obj,
        'profile': profile,
    })


# ---------------------------------------------------------------------------
# Admin: Department Management
# ---------------------------------------------------------------------------

@login_required
@admin_required
def department_list_view(request):
    """List all departments."""
    departments = Department.objects.all()
    query = request.GET.get('q', '')
    if query:
        departments = departments.filter(
            Q(name__icontains=query) | Q(code__icontains=query)
        )
    paginator = Paginator(departments, 15)
    page = request.GET.get('page')
    departments = paginator.get_page(page)
    return render(request, 'accounts/department_list.html', {
        'departments': departments,
        'query': query,
    })


@login_required
@admin_required
def department_create_view(request):
    """Create a new department."""
    form = DepartmentForm()
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save()
            ActivityLog.objects.create(
                user=request.user, action='create',
                model_name='Department', object_id=dept.id,
                object_repr=str(dept), details=f'Created department {dept.name}'
            )
            messages.success(request, f'Department "{dept.name}" created.')
            return redirect('accounts:department_list')
    return render(request, 'accounts/department_form.html', {
        'form': form,
        'title': 'Create Department',
        'button_text': 'Create',
    })


@login_required
@admin_required
def department_edit_view(request, pk):
    """Edit an existing department."""
    dept = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(instance=dept)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=dept)
        if form.is_valid():
            form.save()
            messages.success(request, f'Department "{dept.name}" updated.')
            return redirect('accounts:department_list')
    return render(request, 'accounts/department_form.html', {
        'form': form,
        'title': f'Edit Department: {dept.name}',
        'button_text': 'Save Changes',
    })
