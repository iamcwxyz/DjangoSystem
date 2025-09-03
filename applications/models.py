from django.db import models
from django.utils import timezone
from authentication.models import Employee


class JobApplication(models.Model):
    """Job application model"""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Under Review', 'Under Review'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]
    
    application_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    position_applied = models.CharField(max_length=100)
    resume_file = models.FileField(upload_to='resumes/', null=True, blank=True)
    work_experience = models.TextField()
    education = models.TextField()
    skills = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_date = models.DateTimeField(default=timezone.now)
    processed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    processed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'applications'
    
    def __str__(self):
        return f"{self.application_id} - {self.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.application_id:
            self.application_id = self.generate_application_id()
        super().save(*args, **kwargs)
    
    def generate_application_id(self):
        """Generate next application ID in format APP0001, APP0002, etc."""
        last_app = JobApplication.objects.filter(
            application_id__startswith='APP'
        ).order_by('application_id').last()
        
        if last_app and last_app.application_id:
            try:
                num = int(last_app.application_id[3:]) + 1
            except (ValueError, IndexError):
                num = 1
        else:
            num = 1
        
        return f"APP{num:04d}"