from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import Notification

# Create your views here.

@login_required
def notification_list(request):
    """Show user notifications"""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })

@login_required
def mark_notification_read(request, pk):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.mark_as_read()
    
    if request.GET.get('next'):
        return redirect(request.GET.get('next'))
    return redirect('notifications:notification_list')

@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, _('Всі сповіщення позначено як прочитані.'))
    
    if request.GET.get('next'):
        return redirect(request.GET.get('next'))
    return redirect('notifications:notification_list')
