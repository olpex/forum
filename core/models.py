from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse
from users.models import User

class Section(models.Model):
    title = models.CharField(_('Назва'), max_length=255)
    description = models.TextField(_('Опис'), blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_sections')
    created_at = models.DateTimeField(_('Створено'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Оновлено'), auto_now=True)
    is_active = models.BooleanField(_('Активний'), default=True)
    is_frozen = models.BooleanField(_('Заморожений'), default=False)
    
    class Meta:
        verbose_name = _('Розділ')
        verbose_name_plural = _('Розділи')
        ordering = ['title']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('section_detail', kwargs={'pk': self.pk})
    
    def freeze(self):
        self.is_frozen = True
        self.save()
    
    def unfreeze(self):
        self.is_frozen = False
        self.save()

class Tag(models.Model):
    name = models.CharField(_('Назва'), max_length=100, unique=True)
    created_at = models.DateTimeField(_('Створено'), auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tags')
    
    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('tag_posts', kwargs={'tag_name': self.name})

class PostType(models.Model):
    ANNOUNCEMENT = 'announcement'
    QUESTION = 'question'
    SUGGESTION = 'suggestion'
    MESSAGE = 'message'
    FEEDBACK = 'feedback'
    
    TYPE_CHOICES = [
        (ANNOUNCEMENT, _('Оголошення')),
        (QUESTION, _('Питання')),
        (SUGGESTION, _('Пропозиція')),
        (MESSAGE, _('Повідомлення')),
        (FEEDBACK, _('Відгук')),
    ]
    
    type = models.CharField(_('Тип'), max_length=20, choices=TYPE_CHOICES, unique=True)
    
    class Meta:
        verbose_name = _('Тип посту')
        verbose_name_plural = _('Типи постів')
    
    def __str__(self):
        return self.get_type_display()

class Post(models.Model):
    title = models.CharField(_('Заголовок'), max_length=255)
    content = models.TextField(_('Зміст'))
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(_('Створено'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Оновлено'), auto_now=True)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    post_type = models.ForeignKey(PostType, on_delete=models.SET_NULL, null=True, related_name='posts')
    is_closed = models.BooleanField(_('Закрито'), default=False)
    is_frozen = models.BooleanField(_('Заморожено'), default=False)
    upvotes = models.ManyToManyField(User, related_name='upvoted_posts', blank=True)
    downvotes = models.ManyToManyField(User, related_name='downvoted_posts', blank=True)
    
    class Meta:
        verbose_name = _('Пост')
        verbose_name_plural = _('Пости')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})
    
    def close(self):
        self.is_closed = True
        self.save()
    
    def reopen(self):
        self.is_closed = False
        self.save()
    
    def freeze(self):
        self.is_frozen = True
        self.save()
    
    def unfreeze(self):
        self.is_frozen = False
        self.save()
    
    def upvote(self, user):
        if user in self.downvotes.all():
            self.downvotes.remove(user)
        if user not in self.upvotes.all():
            self.upvotes.add(user)
    
    def downvote(self, user):
        if user in self.upvotes.all():
            self.upvotes.remove(user)
        if user not in self.downvotes.all():
            self.downvotes.add(user)
    
    def remove_vote(self, user):
        if user in self.upvotes.all():
            self.upvotes.remove(user)
        if user in self.downvotes.all():
            self.downvotes.remove(user)
    
    @property
    def vote_score(self):
        return self.upvotes.count() - self.downvotes.count()
    
    @property
    def comment_count(self):
        return self.comments.count()
    
    @property
    def contributors(self):
        """Returns a list of all users who have contributed to this post (author + commenters)"""
        commenters = self.comments.values_list('author', flat=True).distinct()
        contributors = list(commenters)
        if self.author.id not in contributors:
            contributors.append(self.author.id)
        return User.objects.filter(id__in=contributors)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(_('Зміст'))
    created_at = models.DateTimeField(_('Створено'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Оновлено'), auto_now=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    is_frozen = models.BooleanField(_('Заморожено'), default=False)
    upvotes = models.ManyToManyField(User, related_name='upvoted_comments', blank=True)
    downvotes = models.ManyToManyField(User, related_name='downvoted_comments', blank=True)
    
    class Meta:
        verbose_name = _('Коментар')
        verbose_name_plural = _('Коментарі')
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author} on {self.post.title}"
    
    def freeze(self):
        self.is_frozen = True
        self.save()
    
    def unfreeze(self):
        self.is_frozen = False
        self.save()
    
    def upvote(self, user):
        if user in self.downvotes.all():
            self.downvotes.remove(user)
        if user not in self.upvotes.all():
            self.upvotes.add(user)
    
    def downvote(self, user):
        if user in self.upvotes.all():
            self.upvotes.remove(user)
        if user not in self.downvotes.all():
            self.downvotes.add(user)
    
    def remove_vote(self, user):
        if user in self.upvotes.all():
            self.upvotes.remove(user)
        if user in self.downvotes.all():
            self.downvotes.remove(user)
    
    @property
    def vote_score(self):
        return self.upvotes.count() - self.downvotes.count()
    
    @property
    def is_reply(self):
        return self.parent is not None

class ActionLog(models.Model):
    ACTION_CREATE = 'create'
    ACTION_UPDATE = 'update'
    ACTION_DELETE = 'delete'
    ACTION_FREEZE = 'freeze'
    ACTION_UNFREEZE = 'unfreeze'
    ACTION_CLOSE = 'close'
    ACTION_REOPEN = 'reopen'
    
    ACTION_CHOICES = [
        (ACTION_CREATE, _('Створення')),
        (ACTION_UPDATE, _('Оновлення')),
        (ACTION_DELETE, _('Видалення')),
        (ACTION_FREEZE, _('Заморозка')),
        (ACTION_UNFREEZE, _('Розморозка')),
        (ACTION_CLOSE, _('Закриття')),
        (ACTION_REOPEN, _('Відкриття')),
    ]
    
    CONTENT_SECTION = 'section'
    CONTENT_POST = 'post'
    CONTENT_COMMENT = 'comment'
    
    CONTENT_CHOICES = [
        (CONTENT_SECTION, _('Розділ')),
        (CONTENT_POST, _('Пост')),
        (CONTENT_COMMENT, _('Коментар')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions')
    action = models.CharField(_('Дія'), max_length=10, choices=ACTION_CHOICES)
    content_type = models.CharField(_('Тип контенту'), max_length=10, choices=CONTENT_CHOICES)
    content_id = models.PositiveIntegerField(_('ID контенту'))
    timestamp = models.DateTimeField(_('Час'), auto_now_add=True)
    reason = models.TextField(_('Причина'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Журнал дій')
        verbose_name_plural = _('Журнал дій')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.get_action_display()} {self.get_content_type_display()} by {self.user} at {self.timestamp}"
