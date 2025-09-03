from django.db import models
from django.utils import timezone
from authentication.models import Employee
import string
import random


class ChatRoom(models.Model):
    """Chat room model"""
    ROOM_TYPE_CHOICES = [
        ('general', 'General'),
        ('group', 'Group'),
        ('direct', 'Direct Message'),
        ('applicant', 'Applicant Support'),
    ]
    
    room_name = models.CharField(max_length=255)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default='group')
    join_code = models.CharField(max_length=20, unique=True)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'chat_rooms'
    
    def __str__(self):
        return self.room_name
    
    def save(self, *args, **kwargs):
        if not self.join_code:
            self.join_code = self.generate_join_code()
        super().save(*args, **kwargs)
    
    def generate_join_code(self):
        """Generate random join code"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


class ChatMessage(models.Model):
    """Chat message model"""
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='sent_messages')
    sender_type = models.CharField(max_length=20, default='employee')
    message = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['sent_at']
    
    def __str__(self):
        return f"{self.sender.name}: {self.message[:50]}"


class RoomMembership(models.Model):
    """Room membership model"""
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='memberships')
    member = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='room_memberships')
    member_type = models.CharField(max_length=20, default='employee')
    joined_at = models.DateTimeField(default=timezone.now)
    last_read_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'room_memberships'
        unique_together = ['room', 'member']
    
    def __str__(self):
        return f"{self.member.name} in {self.room.room_name}"