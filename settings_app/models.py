from django.db import models
from django.utils import timezone
from authentication.models import Employee


class SystemSetting(models.Model):
    """System settings model"""
    setting_name = models.CharField(max_length=100, unique=True)
    setting_value = models.TextField()
    description = models.TextField(blank=True)
    updated_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'settings'
    
    def __str__(self):
        return f"{self.setting_name}: {self.setting_value[:50]}"