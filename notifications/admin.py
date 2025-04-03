from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Notification, EmailTemplate

# Register your models here.

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'actor', 'created_at', 'is_read', 'is_email_sent')
    list_filter = ('notification_type', 'is_read', 'is_email_sent', 'created_at')
    search_fields = ('recipient__email', 'recipient__first_name', 'recipient__last_name', 
                    'actor__email', 'actor__first_name', 'actor__last_name', 'message')
    readonly_fields = ('recipient', 'notification_type', 'content_id', 'content_type', 
                      'actor', 'message', 'created_at', 'reason')
    fieldsets = (
        (None, {'fields': ('recipient', 'notification_type', 'content_type', 'content_id', 'actor', 'message')}),
        (_('Статус'), {'fields': ('is_read', 'is_email_sent')}),
        (_('Додатково'), {'fields': ('reason', 'created_at')}),
    )

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'notification_type', 'subject')
    list_filter = ('notification_type',)
    search_fields = ('name', 'subject', 'body')
    fieldsets = (
        (None, {'fields': ('name', 'notification_type')}),
        (_('Шаблон'), {'fields': ('subject', 'body')}),
    )
