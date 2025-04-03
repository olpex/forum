from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Section, Tag, PostType, Post, Comment, ActionLog

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'is_active', 'is_frozen')
    list_filter = ('is_active', 'is_frozen', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('title', 'description')}),
        (_('Статус'), {'fields': ('is_active', 'is_frozen')}),
        (_('Інформація'), {'fields': ('created_by', 'created_at', 'updated_at')}),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new section
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_by', 'created_at')
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new tag
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(PostType)
class PostTypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'get_type_display')
    search_fields = ('type',)

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('author', 'created_at', 'updated_at')
    fields = ('author', 'content', 'is_frozen', 'created_at', 'updated_at')
    can_delete = False
    show_change_link = True
    verbose_name = _('Коментар')
    verbose_name_plural = _('Коментарі')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'section', 'created_at', 'is_closed', 'is_frozen', 'comment_count')
    list_filter = ('is_closed', 'is_frozen', 'created_at', 'section', 'post_type')
    search_fields = ('title', 'content', 'author__email', 'author__first_name', 'author__last_name')
    readonly_fields = ('author', 'created_at', 'updated_at', 'upvotes', 'downvotes')
    filter_horizontal = ('tags',)
    fieldsets = (
        (None, {'fields': ('title', 'content', 'section', 'post_type', 'tags')}),
        (_('Статус'), {'fields': ('is_closed', 'is_frozen')}),
        (_('Інформація'), {'fields': ('author', 'created_at', 'updated_at')}),
        (_('Голосування'), {'fields': ('upvotes', 'downvotes')}),
    )
    inlines = [CommentInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new post
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'author', 'post', 'created_at', 'is_frozen')
    list_filter = ('is_frozen', 'created_at')
    search_fields = ('content', 'author__email', 'author__first_name', 'author__last_name', 'post__title')
    readonly_fields = ('author', 'post', 'parent', 'created_at', 'updated_at', 'upvotes', 'downvotes')
    fieldsets = (
        (None, {'fields': ('post', 'parent', 'content')}),
        (_('Статус'), {'fields': ('is_frozen',)}),
        (_('Інформація'), {'fields': ('author', 'created_at', 'updated_at')}),
        (_('Голосування'), {'fields': ('upvotes', 'downvotes')}),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new comment
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'content_type', 'content_id', 'timestamp')
    list_filter = ('action', 'content_type', 'timestamp')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'reason')
    readonly_fields = ('user', 'action', 'content_type', 'content_id', 'timestamp')
    fieldsets = (
        (None, {'fields': ('user', 'action', 'content_type', 'content_id', 'reason', 'timestamp')}),
    )
