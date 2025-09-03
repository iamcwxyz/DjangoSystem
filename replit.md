# Overview

This is a comprehensive Django-based payroll management system designed for federal agencies. The system provides employee management, time tracking, job applications, and various administrative functions with role-based access control. It features a modern web interface with government-style theming and supports multiple user roles including Admin, HR, and Employee.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Framework
The system is built on Django 5.2.5, utilizing Django's built-in features for authentication, ORM, and admin interface. The project follows Django's standard app-based architecture with modular components.

## Database Design
- **Custom User Model**: Extended Django's AbstractUser to create an Employee model with government-specific fields (employee_id, department, position, salary_rate, role, status)
- **Application Management**: JobApplication model handles job applications with file upload support for resumes
- **Chat System**: Real-time communication between employees using ChatRoom and ChatMessage models
- **Settings Management**: Centralized system settings through SystemSetting model
- **Time Tracking**: Attendance system integrated with kiosk functionality

## Authentication & Authorization
- Role-based access control with three primary roles: Admin, HR, and Employee
- Custom authentication views with security logging capabilities
- Session-based authentication with role-specific dashboard routing
- Security event tracking through SecurityLog model

## Frontend Architecture
- Bootstrap 5 for responsive UI components
- Custom government-style CSS with dark theme support
- Template inheritance using Django's template system
- Font Awesome icons for consistent iconography
- Responsive design optimized for both desktop and mobile devices

## File Management
- Django's file handling system for resume uploads
- Static file serving for CSS, JavaScript, and images
- Media file management for user-uploaded content

## Application Structure
- **applications**: Job application management and status tracking
- **authentication**: Custom user model and authentication logic
- **chat_system**: Internal communication system
- **employees**: Employee-specific functionality
- **hr_management**: HR-specific operations
- **kiosk**: Time clock functionality for employee check-in/out
- **security**: Security logging and monitoring
- **settings_app**: System configuration management

## URL Routing
Centralized URL configuration with app-specific URL includes, supporting both public-facing pages (job applications, kiosk) and authenticated user dashboards.

# External Dependencies

## Core Framework
- **Django 5.2.5**: Main web framework
- **django-extensions**: Enhanced Django management commands and utilities
- **crispy-forms & crispy-bootstrap5**: Enhanced form rendering with Bootstrap integration

## Frontend Libraries
- **Bootstrap 5.1.3**: CSS framework for responsive design
- **Font Awesome 6.0.0**: Icon library
- **jQuery**: JavaScript library for enhanced interactions

## Development Tools
- **Django Admin**: Built-in administrative interface
- **Django ORM**: Database abstraction layer
- **Django Templates**: Server-side template rendering

## File Storage
- Django's default file storage system for handling uploaded files (resumes, profile pictures)

## Security Features
- CSRF protection enabled
- Trusted origins configuration for Replit deployment
- Custom security logging for authentication events

## Deployment Configuration
- Configured for Replit environment with appropriate ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS settings
- Environment variable support for sensitive configuration (SECRET_KEY)
- Static and media file serving configuration for development