from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from authentication.models import Employee
from .models import ChatRoom, ChatMessage, RoomMembership
import json


@login_required
def chat_dashboard(request):
    """Communications Center - Main chat dashboard"""
    # Get all employees for direct messaging
    all_employees = Employee.objects.filter(status='Active').exclude(id=request.user.id)
    
    # Get user's chat rooms with member counts
    user_rooms = ChatRoom.objects.filter(
        memberships__member=request.user
    ).annotate(member_count=Count('memberships')).order_by('-created_at')
    
    # Get public/general rooms user is not in
    public_rooms = ChatRoom.objects.filter(
        room_type='general'
    ).exclude(
        memberships__member=request.user
    ).annotate(member_count=Count('memberships'))
    
    context = {
        'all_employees': all_employees,
        'user_rooms': user_rooms,
        'public_rooms': public_rooms,
    }
    return render(request, 'chat_system/dashboard.html', context)


@login_required
def create_room(request):
    """Create new chat room"""
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        room_type = request.POST.get('room_type', 'group')
        
        if room_name:
            try:
                # Create the room
                room = ChatRoom.objects.create(
                    room_name=room_name,
                    room_type=room_type,
                    created_by=request.user
                )
                
                # Add creator as member
                RoomMembership.objects.create(
                    room=room,
                    member=request.user
                )
                
                messages.success(request, f'Chat room "{room_name}" created successfully! Join code: {room.join_code}')
                return redirect('chat_room', room_id=room.id)
                
            except Exception as e:
                messages.error(request, f'Error creating room: {str(e)}')
        else:
            messages.error(request, 'Room name is required.')
    
    return render(request, 'chat_system/create_room.html')


@login_required
def join_room(request):
    """Join chat room with code"""
    if request.method == 'POST':
        join_code = request.POST.get('join_code', '').upper().strip()
        
        if join_code:
            try:
                room = ChatRoom.objects.get(join_code=join_code)
                
                # Check if user is already a member
                if RoomMembership.objects.filter(room=room, member=request.user).exists():
                    messages.info(request, f'You are already a member of "{room.room_name}".')
                    return redirect('chat_room', room_id=room.id)
                
                # Add user to room
                RoomMembership.objects.create(
                    room=room,
                    member=request.user
                )
                
                messages.success(request, f'Successfully joined "{room.room_name}"!')
                return redirect('chat_room', room_id=room.id)
                
            except ChatRoom.DoesNotExist:
                messages.error(request, 'Invalid join code. Please check and try again.')
        else:
            messages.error(request, 'Join code is required.')
    
    return render(request, 'chat_system/join_room.html')


@login_required
def chat_room(request, room_id):
    """Chat room interface"""
    room = get_object_or_404(ChatRoom, id=room_id)
    
    # Check if user is member of this room
    if not RoomMembership.objects.filter(room=room, member=request.user).exists():
        messages.error(request, 'You are not a member of this chat room.')
        return redirect('chat_dashboard')
    
    # Get room messages
    messages_list = ChatMessage.objects.filter(room=room).select_related('sender').order_by('sent_at')
    
    # Get room members
    members = Employee.objects.filter(
        room_memberships__room=room
    ).order_by('name')
    
    # Update last read time
    membership = RoomMembership.objects.get(room=room, member=request.user)
    membership.last_read_at = timezone.now()
    membership.save()
    
    context = {
        'room': room,
        'messages': messages_list,
        'members': members,
    }
    return render(request, 'chat_system/room.html', context)


@login_required
def send_message(request, room_id):
    """Send message to chat room"""
    if request.method == 'POST':
        room = get_object_or_404(ChatRoom, id=room_id)
        
        # Check if user is member
        if not RoomMembership.objects.filter(room=room, member=request.user).exists():
            messages.error(request, 'You are not a member of this chat room.')
            return redirect('chat_dashboard')
        
        message_text = request.POST.get('message', '').strip()
        if message_text:
            ChatMessage.objects.create(
                room=room,
                sender=request.user,
                message=message_text
            )
            
        return redirect('chat_room', room_id=room_id)
    
    return redirect('chat_dashboard')


@login_required
def start_direct_chat(request, employee_id):
    """Start or continue direct chat with another employee"""
    other_employee = get_object_or_404(Employee, id=employee_id, status='Active')
    
    if other_employee == request.user:
        messages.error(request, 'You cannot start a chat with yourself.')
        return redirect('chat_dashboard')
    
    # Check if direct chat already exists
    existing_room = ChatRoom.objects.filter(
        room_type='direct',
        memberships__member=request.user
    ).filter(
        memberships__member=other_employee
    ).first()
    
    if existing_room:
        return redirect('chat_room', room_id=existing_room.id)
    
    # Create new direct message room
    room_name = f"{request.user.name} & {other_employee.name}"
    room = ChatRoom.objects.create(
        room_name=room_name,
        room_type='direct',
        created_by=request.user
    )
    
    # Add both users as members
    RoomMembership.objects.create(room=room, member=request.user)
    RoomMembership.objects.create(room=room, member=other_employee)
    
    return redirect('chat_room', room_id=room.id)


@login_required
def get_messages(request, room_id):
    """Get new messages since timestamp (for auto-refresh)"""
    room = get_object_or_404(ChatRoom, id=room_id)
    
    # Check if user is member
    if not RoomMembership.objects.filter(room=room, member=request.user).exists():
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    since_param = request.GET.get('since', '1970-01-01 00:00:00')
    try:
        since = timezone.datetime.fromisoformat(since_param.replace('Z', '+00:00'))
    except:
        since = timezone.datetime.min
    
    messages_list = ChatMessage.objects.filter(
        room=room,
        sent_at__gt=since
    ).select_related('sender').order_by('sent_at')
    
    messages_data = []
    for msg in messages_list:
        messages_data.append({
            'id': msg.id,
            'sender_name': msg.sender.name,
            'employee_id': msg.sender.employee_id,
            'message': msg.message,
            'sent_at': msg.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_own': msg.sender == request.user,
            'profile_picture': msg.sender.profile_picture.url if msg.sender.profile_picture else None
        })
    
    return JsonResponse(messages_data, safe=False)