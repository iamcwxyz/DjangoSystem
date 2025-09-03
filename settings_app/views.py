from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SystemSetting


@login_required 
def settings_view(request):
    """System settings management"""
    if not request.user.is_admin:
        messages.error(request, 'Access denied. Only administrators can modify system settings.')
        return redirect('home')
    
    if request.method == 'POST':
        # Update settings
        for key, value in request.POST.items():
            if key != 'csrfmiddlewaretoken':
                setting, created = SystemSetting.objects.get_or_create(
                    setting_name=key,
                    defaults={'setting_value': value, 'updated_by': request.user}
                )
                if not created:
                    setting.setting_value = value
                    setting.updated_by = request.user
                    setting.save()
        
        messages.success(request, 'Settings updated successfully.')
        return redirect('settings')
    
    # Get current settings
    settings = SystemSetting.objects.all()
    settings_dict = {setting.setting_name: setting.setting_value for setting in settings}
    
    # Default settings if not exists
    default_settings = {
        'company_name': 'Federal Agency',
        'max_leave_days': '30',
        'working_hours_per_day': '8',
        'overtime_rate': '1.5',
        'enable_notifications': 'true',
        'backup_frequency': 'daily',
        'session_timeout': '8',
    }
    
    # Merge with defaults
    for key, default_value in default_settings.items():
        if key not in settings_dict:
            settings_dict[key] = default_value
    
    context = {
        'settings': settings_dict,
    }
    return render(request, 'settings_app/settings.html', context)