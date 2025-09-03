from django.urls import path
from . import views

urlpatterns = [
    path('punch/', views.punch_view, name='kiosk_punch'),
]