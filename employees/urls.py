from django.urls import path
from . import views

urlpatterns = [
    path('', views.employee_list, name='employee_list'),
    path('add/', views.employee_add, name='employee_add'),
    path('edit/<int:employee_id>/', views.employee_edit, name='employee_edit'),
    path('delete/<int:employee_id>/', views.employee_delete, name='employee_delete'),
    path('reports/', views.reports_view, name='reports'),
    path('security-logs/', views.security_logs_view, name='security_logs'),
]