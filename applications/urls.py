from django.urls import path
from . import views

urlpatterns = [
    path('apply/', views.apply_view, name='apply'),
    path('apply/submit/', views.submit_application, name='submit_application'),
    path('apply/status/', views.check_status, name='check_status'),
    path('apply/status/check/', views.status_lookup, name='status_lookup'),
    path('hr/applications/', views.manage_applications, name='manage_applications'),
    path('hr/applications/<int:app_id>/', views.view_application, name='view_application'),
    path('hr/applications/<int:app_id>/update/', views.update_application_status, name='update_application_status'),
]