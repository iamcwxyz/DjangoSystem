from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from authentication.models import Employee, SecurityLog
from django.contrib.auth.hashers import make_password
import os


@login_required
def employee_list(request):
    """Display list of all employees"""
    if not request.user.is_hr:
        messages.error(request, 'Access denied. Insufficient permissions.')
        return redirect('home')
    
    search_query = request.GET.get('search', '')
    employees = Employee.objects.all().order_by('name')
    
    if search_query:
        employees = employees.filter(
            Q(name__icontains=search_query) |
            Q(employee_id__icontains=search_query) |
            Q(department__icontains=search_query) |
            Q(position__icontains=search_query)
        ).order_by('name')
    
    # Pagination
    paginator = Paginator(employees, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'employees': page_obj,
        'search_query': search_query,
        'total_employees': employees.count()
    }
    return render(request, 'employees/list.html', context)


@login_required
def employee_add(request):
    """Add new employee"""
    if not request.user.is_hr:
        messages.error(request, 'Access denied. Insufficient permissions.')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            # Get form data
            username = request.POST.get('username')
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            department = request.POST.get('department')
            position = request.POST.get('position')
            salary_rate = request.POST.get('salary_rate', 0)
            role = request.POST.get('role', 'Employee')
            password = request.POST.get('password')
            profile_picture = request.FILES.get('profile_picture')
            
            # Check if username already exists
            if Employee.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
                return render(request, 'employees/add.html')
            
            # Create employee
            employee = Employee.objects.create(
                username=username,
                name=name,
                email=email,
                phone=phone,
                department=department,
                position=position,
                salary_rate=float(salary_rate) if salary_rate else 0.00,
                role=role,
                password=make_password(password)
            )
            
            if profile_picture:
                employee.profile_picture = profile_picture
                employee.save()
            
            # Log security event
            SecurityLog.objects.create(
                event_type='SYSTEM_ACCESS',
                user=request.user,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                event_description=f"New employee {employee.name} (ID: {employee.employee_id}) created by {request.user.name}"
            )
            
            messages.success(request, f'Employee {employee.name} created successfully with ID: {employee.employee_id}')
            return redirect('employee_list')
            
        except Exception as e:
            messages.error(request, f'Error creating employee: {str(e)}')
    
    return render(request, 'employees/add.html')


@login_required
def employee_edit(request, employee_id):
    """Edit existing employee"""
    if not request.user.is_hr:
        messages.error(request, 'Access denied. Insufficient permissions.')
        return redirect('home')
    
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        try:
            # Update employee data
            employee.name = request.POST.get('name')
            employee.email = request.POST.get('email')
            employee.phone = request.POST.get('phone')
            employee.department = request.POST.get('department')
            employee.position = request.POST.get('position')
            salary_rate = request.POST.get('salary_rate')
            if salary_rate:
                employee.salary_rate = float(salary_rate)
            employee.role = request.POST.get('role', 'Employee')
            employee.status = request.POST.get('status', 'Active')
            
            # Handle profile picture
            if 'profile_picture' in request.FILES:
                # Delete old picture if exists
                if employee.profile_picture:
                    old_path = employee.profile_picture.path
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                employee.profile_picture = request.FILES['profile_picture']
            
            employee.save()
            
            # Log security event
            SecurityLog.objects.create(
                event_type='PROFILE_UPDATE',
                user=request.user,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                event_description=f"Employee {employee.name} (ID: {employee.employee_id}) updated by {request.user.name}"
            )
            
            messages.success(request, f'Employee {employee.name} updated successfully.')
            return redirect('employee_list')
            
        except Exception as e:
            messages.error(request, f'Error updating employee: {str(e)}')
    
    context = {'employee': employee}
    return render(request, 'employees/edit.html', context)


@login_required
def employee_delete(request, employee_id):
    """Delete employee"""
    if not request.user.is_admin:
        messages.error(request, 'Access denied. Only administrators can delete employees.')
        return redirect('employee_list')
    
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        try:
            employee_name = employee.name
            employee_id_str = employee.employee_id
            
            # Delete profile picture if exists
            if employee.profile_picture:
                picture_path = employee.profile_picture.path
                if os.path.exists(picture_path):
                    os.remove(picture_path)
            
            employee.delete()
            
            # Log security event
            SecurityLog.objects.create(
                event_type='SYSTEM_ACCESS',
                user=request.user,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                event_description=f"Employee {employee_name} (ID: {employee_id_str}) deleted by {request.user.name}"
            )
            
            messages.success(request, f'Employee {employee_name} deleted successfully.')
            return redirect('employee_list')
            
        except Exception as e:
            messages.error(request, f'Error deleting employee: {str(e)}')
    
    context = {'employee': employee}
    return render(request, 'employees/delete.html', context)


@login_required
def reports_view(request):
    """Generate various reports"""
    if not request.user.is_hr:
        messages.error(request, 'Access denied. Insufficient permissions.')
        return redirect('home')
    
    # Calculate statistics
    total_employees = Employee.objects.filter(status='Active').count()
    total_departments = Employee.objects.values('department').distinct().count()
    
    # Department-wise breakdown
    departments = Employee.objects.values('department').distinct()
    dept_stats = []
    for dept in departments:
        if dept['department']:
            count = Employee.objects.filter(department=dept['department'], status='Active').count()
            dept_stats.append({
                'name': dept['department'],
                'count': count
            })
    
    # Role-wise breakdown
    role_stats = []
    for role_choice in Employee.ROLE_CHOICES:
        count = Employee.objects.filter(role=role_choice[0], status='Active').count()
        role_stats.append({
            'name': role_choice[1],
            'count': count
        })
    
    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'dept_stats': dept_stats,
        'role_stats': role_stats,
    }
    return render(request, 'employees/reports.html', context)


@login_required
def security_logs_view(request):
    """View security logs"""
    if not request.user.is_admin:
        messages.error(request, 'Access denied. Only administrators can view security logs.')
        return redirect('home')
    
    logs = SecurityLog.objects.all().order_by('-timestamp')
    
    # Pagination
    paginator = Paginator(logs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'logs': page_obj,
        'total_logs': logs.count()
    }
    return render(request, 'employees/security_logs.html', context)
