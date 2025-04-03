from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User

class Notification(models.Model):
    NOTIFICATION_SECTION_CREATE = 'section_create'
    NOTIFICATION_SECTION_UPDATE = 'section_update'
    NOTIFICATION_POST_CREATE = 'post_create'
    NOTIFICATION_POST_UPDATE = 'post_update'
    NOTIFICATION_POST_CLOSE = 'post_close'
    NOTIFICATION_POST_DELETE = 'post_delete'
    NOTIFICATION_POST_FREEZE = 'post_freeze'
    NOTIFICATION_COMMENT_CREATE = 'comment_create'
    NOTIFICATION_COMMENT_UPDATE = 'comment_update'
    NOTIFICATION_COMMENT_DELETE = 'comment_delete'
    NOTIFICATION_COMMENT_FREEZE = 'comment_freeze'
    NOTIFICATION_USER_BAN = 'user_ban'
    NOTIFICATION_USER_UNBAN = 'user_unban'
    NOTIFICATION_USER_FREEZE = 'user_freeze'
    NOTIFICATION_USER_UNFREEZE = 'user_unfreeze'
    NOTIFICATION_USER_DELETE = 'user_delete'
    
    NOTIFICATION_TYPES = [
        (NOTIFICATION_SECTION_CREATE, _('Створення розділу')),
        (NOTIFICATION_SECTION_UPDATE, _('Оновлення розділу')),
        (NOTIFICATION_POST_CREATE, _('Створення посту')),
        (NOTIFICATION_POST_UPDATE, _('Оновлення посту')),
        (NOTIFICATION_POST_CLOSE, _('Закриття посту')),
        (NOTIFICATION_POST_DELETE, _('Видалення посту')),
        (NOTIFICATION_POST_FREEZE, _('Заморозка посту')),
        (NOTIFICATION_COMMENT_CREATE, _('Створення коментаря')),
        (NOTIFICATION_COMMENT_UPDATE, _('Оновлення коментаря')),
        (NOTIFICATION_COMMENT_DELETE, _('Видалення коментаря')),
        (NOTIFICATION_COMMENT_FREEZE, _('Заморозка коментаря')),
        (NOTIFICATION_USER_BAN, _('Блокування користувача')),
        (NOTIFICATION_USER_UNBAN, _('Розблокування користувача')),
        (NOTIFICATION_USER_FREEZE, _('Заморозка користувача')),
        (NOTIFICATION_USER_UNFREEZE, _('Розморозка користувача')),
        (NOTIFICATION_USER_DELETE, _('Видалення користувача')),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(_('Тип сповіщення'), max_length=20, choices=NOTIFICATION_TYPES)
    content_id = models.PositiveIntegerField(_('ID контенту'), null=True, blank=True)
    content_type = models.CharField(_('Тип контенту'), max_length=20, null=True, blank=True)
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions_notifications')
    message = models.TextField(_('Повідомлення'))
    created_at = models.DateTimeField(_('Створено'), auto_now_add=True)
    is_read = models.BooleanField(_('Прочитано'), default=False)
    is_email_sent = models.BooleanField(_('Email надіслано'), default=False)
    reason = models.TextField(_('Причина'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Сповіщення')
        verbose_name_plural = _('Сповіщення')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_notification_type_display()} для {self.recipient}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save()
    
    def mark_as_email_sent(self):
        self.is_email_sent = True
        self.save()

class EmailTemplate(models.Model):
    name = models.CharField(_('Назва'), max_length=100, unique=True)
    subject = models.CharField(_('Тема'), max_length=255)
    body = models.TextField(_('Текст'))
    notification_type = models.CharField(_('Тип сповіщення'), max_length=20, choices=Notification.NOTIFICATION_TYPES)
    
    class Meta:
        verbose_name = _('Шаблон email')
        verbose_name_plural = _('Шаблони email')
    
    def __str__(self):
        return self.name
