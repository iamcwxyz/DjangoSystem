from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Employee, SecurityLog
from django.utils import timezone


def login_view(request):
    """Login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None and user.status == 'Active':
            login(request, user)
            
            # Log successful login
            SecurityLog.objects.create(
                event_type='LOGIN_SUCCESS',
                user=user,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                event_description=f"User {user.username} logged in successfully"
            )
            
            messages.success(request, f'Welcome back, {user.name}!')
            
            # Redirect based on role
            if user.role == 'Admin':
                return redirect('admin_dashboard')
            elif user.role == 'HR':
                return redirect('hr_dashboard')
            elif user.role == 'Employee':
                return redirect('employee_dashboard')
            else:
                return redirect('home')
        else:
            # Log failed login
            SecurityLog.objects.create(
                event_type='LOGIN_FAILED',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                event_description=f"Failed login attempt for username: {username}"
            )
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'authentication/login.html')


def logout_view(request):
    """Logout view"""
    if request.user.is_authenticated:
        SecurityLog.objects.create(
            event_type='LOGOUT',
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            event_description=f"User {request.user.username} logged out"
        )
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


def home_view(request):
    """Home page view"""
    if request.user.is_authenticated:
        # Redirect authenticated users to their dashboards
        if request.user.role == 'Admin':
            return redirect('admin_dashboard')
        elif request.user.role == 'HR':
            return redirect('hr_dashboard')
        elif request.user.role == 'Employee':
            return redirect('employee_dashboard')
    
    return render(request, 'home.html')


@login_required
def admin_dashboard(request):
    """Admin dashboard"""
    if not request.user.is_admin:
        messages.error(request, 'Access denied. Insufficient permissions.')
        return redirect('home')
    
    # Get statistics
    total_employees = Employee.objects.filter(status='Active').count()
    total_attendance_today = 0  # TODO: Calculate today's attendance
    pending_leaves = 0  # TODO: Calculate pending leaves
    
    context = {
        'total_employees': total_employees,
        'total_attendance_today': total_attendance_today,
        'pending_leaves': pending_leaves,
    }
    return render(request, 'admin/dashboard.html', context)


@login_required
def hr_dashboard(request):
    """HR dashboard"""
    if not request.user.is_hr:
        messages.error(request, 'Access denied. Insufficient permissions.')
        return redirect('home')
    
    return render(request, 'hr/dashboard.html')


@login_required
def employee_dashboard(request):
    """Employee dashboard"""
    if not request.user.is_employee:
        messages.error(request, 'Access denied. Insufficient permissions.')
        return redirect('home')
    
    return render(request, 'employee/dashboard.html')