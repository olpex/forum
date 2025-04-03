from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserAction

class UserActionInline(admin.TabularInline):
    model = UserAction
    fk_name = 'user'
    extra = 0
    readonly_fields = ('action', 'actor', 'reason', 'timestamp')
    can_delete = False
    verbose_name = _('Дія над користувачем')
    verbose_name_plural = _('Дії над користувачем')

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_frozen', 'is_banned')
    list_filter = ('role', 'is_active', 'is_frozen', 'is_banned')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Особиста інформація'), {'fields': ('first_name', 'last_name', 'username')}),
        (_('Дозволи'), {'fields': ('role', 'is_active', 'is_frozen', 'is_banned', 'ban_reason', 'ban_until')}),
        (_('Важливі дати'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'username', 'password1', 'password2', 'role'),
        }),
    )
    inlines = [UserActionInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new user
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(UserAction)
class UserActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'actor', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__email', 'actor__email', 'reason')
    readonly_fields = ('user', 'actor', 'action', 'timestamp')
    fieldsets = (
        (None, {'fields': ('user', 'actor', 'action', 'reason', 'timestamp')}),
    )
