from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone

from .models import Notification, EmailTemplate
from users.models import User
from core.models import Post, Comment, Section

def create_notification(notification_type, recipient, actor, content_type=None, content_id=None, message=None, reason=None):
    """
    Create a notification and send an email
    """
    notification = Notification.objects.create(
        notification_type=notification_type,
        recipient=recipient,
        actor=actor,
        content_type=content_type,
        content_id=content_id,
        message=message or '',
        reason=reason
    )
    
    # Send email notification
    send_notification_email(notification)
    
    return notification

def send_notification_email(notification):
    """
    Send an email for a notification
    """
    # Get email template
    try:
        template = EmailTemplate.objects.get(notification_type=notification.notification_type)
    except EmailTemplate.DoesNotExist:
        # Use default template if specific one doesn't exist
        subject = _('Нове сповіщення на форумі')
        message = notification.message
    else:
        subject = template.subject
        message = template.body.format(
            recipient_name=f"{notification.recipient.first_name} {notification.recipient.last_name}",
            actor_name=f"{notification.actor.first_name} {notification.actor.last_name}",
            message=notification.message,
            reason=notification.reason or '',
            date=timezone.now().strftime('%d.%m.%Y %H:%M'),
            content_type=notification.content_type or '',
            content_id=notification.content_id or '',
        )
    
    # Send email
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [notification.recipient.email],
        fail_silently=False,
    )
    
    # Mark notification as email sent
    notification.mark_as_email_sent()

def notify_post_creation(post):
    """
    Notify section administrators about new post
    """
    # Notify section creator
    if post.section.created_by != post.author:
        create_notification(
            notification_type=Notification.NOTIFICATION_POST_CREATE,
            recipient=post.section.created_by,
            actor=post.author,
            content_type='post',
            content_id=post.id,
            message=_(f'Новий пост "{post.title}" було створено в розділі "{post.section.title}".')
        )
    
    # Notify superadmins
    for superadmin in User.objects.filter(role=User.SUPERADMIN):
        if superadmin != post.author and superadmin != post.section.created_by:
            create_notification(
                notification_type=Notification.NOTIFICATION_POST_CREATE,
                recipient=superadmin,
                actor=post.author,
                content_type='post',
                content_id=post.id,
                message=_(f'Новий пост "{post.title}" було створено в розділі "{post.section.title}".')
            )

def notify_post_update(post, actor):
    """
    Notify post author and contributors about post update
    """
    # Notify post author if not the actor
    if post.author != actor:
        create_notification(
            notification_type=Notification.NOTIFICATION_POST_UPDATE,
            recipient=post.author,
            actor=actor,
            content_type='post',
            content_id=post.id,
            message=_(f'Пост "{post.title}" було оновлено.')
        )
    
    # Notify all contributors
    for contributor in post.contributors:
        if contributor != actor and contributor != post.author:
            create_notification(
                notification_type=Notification.NOTIFICATION_POST_UPDATE,
                recipient=contributor,
                actor=actor,
                content_type='post',
                content_id=post.id,
                message=_(f'Пост "{post.title}", в якому ви брали участь, було оновлено.')
            )

def notify_post_close(post, actor):
    """
    Notify post author and contributors about post closure
    """
    # Notify post author if not the actor
    if post.author != actor:
        create_notification(
            notification_type=Notification.NOTIFICATION_POST_CLOSE,
            recipient=post.author,
            actor=actor,
            content_type='post',
            content_id=post.id,
            message=_(f'Пост "{post.title}" було закрито.')
        )
    
    # Notify all contributors
    for contributor in post.contributors:
        if contributor != actor and contributor != post.author:
            create_notification(
                notification_type=Notification.NOTIFICATION_POST_CLOSE,
                recipient=contributor,
                actor=actor,
                content_type='post',
                content_id=post.id,
                message=_(f'Пост "{post.title}", в якому ви брали участь, було закрито.')
            )

def notify_post_freeze(post, actor, reason=None):
    """
    Notify post author and contributors about post freeze
    """
    # Notify post author if not the actor
    if post.author != actor:
        create_notification(
            notification_type=Notification.NOTIFICATION_POST_FREEZE,
            recipient=post.author,
            actor=actor,
            content_type='post',
            content_id=post.id,
            message=_(f'Пост "{post.title}" було заморожено.'),
            reason=reason
        )
    
    # Notify all contributors
    for contributor in post.contributors:
        if contributor != actor and contributor != post.author:
            create_notification(
                notification_type=Notification.NOTIFICATION_POST_FREEZE,
                recipient=contributor,
                actor=actor,
                content_type='post',
                content_id=post.id,
                message=_(f'Пост "{post.title}", в якому ви брали участь, було заморожено.'),
                reason=reason
            )

def notify_post_delete(post, actor, reason=None):
    """
    Notify post author and contributors about post deletion
    """
    # Notify post author if not the actor
    if post.author != actor:
        create_notification(
            notification_type=Notification.NOTIFICATION_POST_DELETE,
            recipient=post.author,
            actor=actor,
            content_type='post',
            content_id=post.id,
            message=_(f'Пост "{post.title}" було видалено.'),
            reason=reason
        )
    
    # Notify all contributors
    for contributor in post.contributors:
        if contributor != actor and contributor != post.author:
            create_notification(
                notification_type=Notification.NOTIFICATION_POST_DELETE,
                recipient=contributor,
                actor=actor,
                content_type='post',
                content_id=post.id,
                message=_(f'Пост "{post.title}", в якому ви брали участь, було видалено.'),
                reason=reason
            )

def notify_comment_creation(comment):
    """
    Notify post author and contributors about new comment
    """
    # Notify post author if not the commenter
    if comment.post.author != comment.author:
        create_notification(
            notification_type=Notification.NOTIFICATION_COMMENT_CREATE,
            recipient=comment.post.author,
            actor=comment.author,
            content_type='comment',
            content_id=comment.id,
            message=_(f'Новий коментар додано до вашого посту "{comment.post.title}".')
        )
    
    # If this is a reply, notify parent comment author
    if comment.parent and comment.parent.author != comment.author:
        create_notification(
            notification_type=Notification.NOTIFICATION_COMMENT_CREATE,
            recipient=comment.parent.author,
            actor=comment.author,
            content_type='comment',
            content_id=comment.id,
            message=_(f'Нова відповідь на ваш коментар у пості "{comment.post.title}".')
        )
    
    # Notify all other contributors
    for contributor in comment.post.contributors:
        if contributor != comment.author and contributor != comment.post.author and (not comment.parent or contributor != comment.parent.author):
            create_notification(
                notification_type=Notification.NOTIFICATION_COMMENT_CREATE,
                recipient=contributor,
                actor=comment.author,
                content_type='comment',
                content_id=comment.id,
                message=_(f'Новий коментар додано до посту "{comment.post.title}", в якому ви брали участь.')
            )

def notify_user_ban(user, actor, reason=None):
    """
    Notify user about ban
    """
    create_notification(
        notification_type=Notification.NOTIFICATION_USER_BAN,
        recipient=user,
        actor=actor,
        content_type='user',
        content_id=user.id,
        message=_('Ваш обліковий запис було заблоковано.'),
        reason=reason
    )

def notify_user_freeze(user, actor, reason=None):
    """
    Notify user about account freeze
    """
    create_notification(
        notification_type=Notification.NOTIFICATION_USER_FREEZE,
        recipient=user,
        actor=actor,
        content_type='user',
        content_id=user.id,
        message=_('Ваш обліковий запис було заморожено.'),
        reason=reason
    )

def notify_section_creation(section):
    """
    Notify superadmins about new section
    """
    # Notify all superadmins except the creator
    for superadmin in User.objects.filter(role=User.SUPERADMIN):
        if superadmin != section.created_by:
            create_notification(
                notification_type=Notification.NOTIFICATION_SECTION_CREATE,
                recipient=superadmin,
                actor=section.created_by,
                content_type='section',
                content_id=section.id,
                message=_(f'Новий розділ "{section.title}" було створено.')
            )
