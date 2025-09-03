from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.utils import timezone
from .models import JobApplication
from authentication.models import Employee
import os


def apply_view(request):
    """Public job application form"""
    return render(request, 'applications/apply.html')


def submit_application(request):
    """Submit a new job application"""
    if request.method == 'POST':
        try:
            # Handle file upload
            resume_file = None
            if 'resume' in request.FILES:
                file = request.FILES['resume']
                if file and allowed_file(file.name):
                    # Generate unique filename
                    filename = f"resume_{timezone.now().strftime('%Y%m%d_%H%M%S')}_{file.name}"
                    resume_file = default_storage.save(f'resumes/{filename}', file)
            
            # Create application
            application = JobApplication.objects.create(
                full_name=request.POST['full_name'],
                email=request.POST['email'],
                phone=request.POST['phone'],
                address=request.POST['address'],
                position_applied=request.POST['position'],
                resume_file=resume_file,
                work_experience=request.POST['work_experience'],
                education=request.POST['education'],
                skills=request.POST['skills'],
                status='Pending'
            )
            
            return render(request, 'applications/application_success.html', {
                'application_id': application.application_id
            })
            
        except Exception as e:
            messages.error(request, f'Error submitting application: {str(e)}')
            return redirect('apply')
    
    return redirect('apply')


def check_status(request):
    """Check application status form"""
    return render(request, 'applications/check_status.html')


def status_lookup(request):
    """Look up application status"""
    if request.method == 'POST':
        app_id = request.POST.get('application_id')
        
        try:
            application = JobApplication.objects.get(application_id=app_id)
            return render(request, 'applications/status_result.html', {
                'application': application
            })
        except JobApplication.DoesNotExist:
            messages.error(request, 'Application ID not found. Please check your ID and try again.')
            return redirect('check_status')
    
    return redirect('check_status')


@login_required
def manage_applications(request):
    """HR view for managing job applications"""
    if not request.user.is_hr:
        messages.error(request, 'Access denied. Insufficient permissions.')
        return redirect('home')
    
    # Order by status priority and date
    applications = JobApplication.objects.all().order_by('status', '-applied_date')
    
    return render(request, 'applications/manage_applications.html', {
        'applications': applications
    })


@login_required
def view_application(request, app_id):
    """View detailed application"""
    if not request.user.is_hr:
        messages.error(request, 'Access denied. Insufficient permissions.')
        return redirect('home')
    
    application = get_object_or_404(JobApplication, id=app_id)
    
    return render(request, 'applications/view_application.html', {
        'application': application
    })


@login_required
def update_application_status(request, app_id):
    """Update application status"""
    if not request.user.is_hr:
        messages.error(request, 'Access denied. Insufficient permissions.')
        return redirect('home')
    
    if request.method == 'POST':
        application = get_object_or_404(JobApplication, id=app_id)
        
        application.status = request.POST['status']
        application.notes = request.POST.get('notes', '')
        application.processed_by = request.user
        application.processed_date = timezone.now()
        application.save()
        
        messages.success(request, 'Application status updated successfully!')
        return redirect('view_application', app_id=app_id)
    
    return redirect('view_application', app_id=app_id)


def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS