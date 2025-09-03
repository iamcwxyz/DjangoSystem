from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, date
from authentication.models import Employee, Attendance


def punch_view(request):
    """Kiosk time punch view for employees to clock in/out"""
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id', '').strip().upper()
        
        if not employee_id:
            messages.error(request, 'Employee ID is required')
            return render(request, 'kiosk/punch.html')
        
        # Search for employee by employee_id
        try:
            employee = Employee.objects.get(employee_id=employee_id, status='Active')
        except Employee.DoesNotExist:
            messages.error(request, 'Employee ID not found or inactive')
            return render(request, 'kiosk/punch.html')
        
        today = date.today()
        now_time = datetime.now().time()
        
        # Check if there's already an attendance record for today
        attendance_record = Attendance.objects.filter(
            employee=employee, 
            date=today
        ).first()
        
        context = {
            'employee': employee,
            'today': today,
        }
        
        if not attendance_record:
            # Time-in
            Attendance.objects.create(
                employee=employee,
                date=today,
                time_in=now_time
            )
            context.update({
                'message': f"✅ TIME-IN recorded at {now_time.strftime('%H:%M:%S')}",
                'message_type': "success",
                'time_in': now_time,
                'time_out': None
            })
        else:
            if not attendance_record.time_out:
                # Time-out
                attendance_record.time_out = now_time
                attendance_record.save()
                context.update({
                    'message': f"✅ TIME-OUT recorded at {now_time.strftime('%H:%M:%S')}",
                    'message_type': "success",
                    'time_in': attendance_record.time_in,
                    'time_out': now_time
                })
            else:
                context.update({
                    'message': "ℹ️ Already timed in and out today",
                    'message_type': "info",
                    'time_in': attendance_record.time_in,
                    'time_out': attendance_record.time_out
                })
        
        return render(request, 'kiosk/punch.html', context)
    
    return render(request, 'kiosk/punch.html')