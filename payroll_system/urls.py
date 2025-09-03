"""
URL configuration for payroll_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home'),
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home'),
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from authentication.views import home_view, login_view, logout_view, admin_dashboard, hr_dashboard, employee_dashboard

urlpatterns = [
    path('django-admin/', admin.site.urls),  # Changed to avoid conflict
    path('', home_view, name='home'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('hr/dashboard/', hr_dashboard, name='hr_dashboard'),
    path('employee/dashboard/', employee_dashboard, name='employee_dashboard'),
    path('kiosk/', include('kiosk.urls')),
    path('applications/', include('applications.urls')),
    path('chat/', include('chat_system.urls')),
    path('settings/', include('settings_app.urls')),
    path('employees/', include('employees.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)