from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid


class Employee(AbstractUser):
    """Custom User model representing an Employee"""
    ROLE_CHOICES = [
        ('Admin', 'Administrator'),
        ('HR', 'Human Resources'),
        ('Employee', 'Employee'),
    ]
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Suspended', 'Suspended'),
    ]
    
    # Override default fields
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True, null=True)
    
    # Custom fields from Flask system
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    salary_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Employee')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    nfc_id = models.CharField(max_length=100, blank=True, null=True)
    qr_code_path = models.CharField(max_length=255, blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employees'
    
    def __str__(self):
        return f"{self.employee_id} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.employee_id:
            self.employee_id = self.generate_employee_id()
        super().save(*args, **kwargs)
    
    def generate_employee_id(self):
        """Generate next employee ID in format EMP001, EMP002, etc."""
        last_employee = Employee.objects.filter(
            employee_id__startswith='EMP'
        ).order_by('employee_id').last()
        
        if last_employee and last_employee.employee_id:
            try:
                num = int(last_employee.employee_id[3:]) + 1
            except (ValueError, IndexError):
                num = 1
        else:
            num = 1
        
        return f"EMP{num:03d}"
    
    @property
    def is_admin(self):
        return self.role == 'Admin'
    
    @property
    def is_hr(self):
        return self.role in ['Admin', 'HR']
    
    @property
    def is_employee(self):
        return self.role == 'Employee'


class Attendance(models.Model):
    """Employee attendance records"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'attendance'
        unique_together = ['employee', 'date']
    
    def __str__(self):
        return f"{self.employee.name} - {self.date}"


class Leave(models.Model):
    """Employee leave requests"""
    LEAVE_TYPE_CHOICES = [
        ('Sick', 'Sick Leave'),
        ('Vacation', 'Vacation Leave'),
        ('Emergency', 'Emergency Leave'),
        ('Unpaid', 'Unpaid Leave'),
    ]
    
    DURATION_CHOICES = [
        ('Full', 'Full Day'),
        ('Half', 'Half Day'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    duration = models.CharField(max_length=10, choices=DURATION_CHOICES, default='Full')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_at = models.DateTimeField(default=timezone.now)
    processed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_leaves')
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'leaves'
    
    def __str__(self):
        return f"{self.employee.name} - {self.type} ({self.start_date} to {self.end_date})"


class Payroll(models.Model):
    """Employee payroll records"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_records')
    period = models.CharField(max_length=20)  # e.g., "2025-01" or "Jan-2025"
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    overtime = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'payroll'
        unique_together = ['employee', 'period']
    
    def __str__(self):
        return f"{self.employee.name} - {self.period}"


class SecurityLog(models.Model):
    """Security audit trail"""
    EVENT_TYPE_CHOICES = [
        ('LOGIN_SUCCESS', 'Successful Login'),
        ('LOGIN_FAILED', 'Failed Login'),
        ('LOGOUT', 'Logout'),
        ('SESSION_TIMEOUT', 'Session Timeout'),
        ('PASSWORD_CHANGE', 'Password Change'),
        ('PROFILE_UPDATE', 'Profile Update'),
        ('DATA_EXPORT', 'Data Export'),
        ('MANUAL_BACKUP', 'Manual Backup'),
        ('SYSTEM_ACCESS', 'System Access'),
    ]
    
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    user = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    event_description = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'security_logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.event_type} - {self.user} - {self.timestamp}"