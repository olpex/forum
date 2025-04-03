from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    SUPERADMIN = 'superadmin'
    ADMIN = 'admin'
    STUDENT = 'student'
    
    ROLE_CHOICES = [
        (SUPERADMIN, _('Суперадміністратор')),
        (ADMIN, _('Адміністратор')),
        (STUDENT, _('Студент')),
    ]
    
    first_name = models.CharField(_('Ім\'я'), max_length=150)
    last_name = models.CharField(_('Прізвище'), max_length=150)
    email = models.EmailField(_('Email адреса'), unique=True)
    role = models.CharField(_('Роль'), max_length=10, choices=ROLE_CHOICES, default=STUDENT)
    is_active = models.BooleanField(_('Активний'), default=True)
    is_frozen = models.BooleanField(_('Заморожений'), default=False)
    is_banned = models.BooleanField(_('Заблокований'), default=False)
    ban_reason = models.TextField(_('Причина блокування'), blank=True, null=True)
    ban_until = models.DateTimeField(_('Заблоковано до'), blank=True, null=True)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='created_users')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = _('Користувач')
        verbose_name_plural = _('Користувачі')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def is_superadmin(self):
        return self.role == self.SUPERADMIN
    
    def is_admin(self):
        return self.role == self.ADMIN
    
    def is_student(self):
        return self.role == self.STUDENT
    
    def ban(self, reason=None, days=None):
        self.is_banned = True
        self.ban_reason = reason
        if days:
            self.ban_until = timezone.now() + timedelta(days=days)
        self.save()
    
    def unban(self):
        self.is_banned = False
        self.ban_reason = None
        self.ban_until = None
        self.save()
    
    def freeze(self):
        self.is_frozen = True
        self.save()
    
    def unfreeze(self):
        self.is_frozen = False
        self.save()

class UserAction(models.Model):
    ACTION_BAN = 'ban'
    ACTION_UNBAN = 'unban'
    ACTION_FREEZE = 'freeze'
    ACTION_UNFREEZE = 'unfreeze'
    ACTION_DELETE = 'delete'
    
    ACTION_CHOICES = [
        (ACTION_BAN, _('Блокування')),
        (ACTION_UNBAN, _('Розблокування')),
        (ACTION_FREEZE, _('Заморозка')),
        (ACTION_UNFREEZE, _('Розморозка')),
        (ACTION_DELETE, _('Видалення')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions_received')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions_performed')
    action = models.CharField(_('Дія'), max_length=10, choices=ACTION_CHOICES)
    reason = models.TextField(_('Причина'), blank=True, null=True)
    timestamp = models.DateTimeField(_('Час'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Дія над користувачем')
        verbose_name_plural = _('Дії над користувачами')
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.user} by {self.actor} at {self.timestamp}"
