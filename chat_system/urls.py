from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_dashboard, name='chat_dashboard'),
    path('create/', views.create_room, name='create_room'),
    path('join/', views.join_room, name='join_room'),
    path('room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('room/<int:room_id>/send/', views.send_message, name='send_message'),
    path('direct/<int:employee_id>/', views.start_direct_chat, name='start_direct_chat'),
    path('room/<int:room_id>/messages/', views.get_messages, name='get_messages'),
]