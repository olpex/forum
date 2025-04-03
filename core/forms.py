from django import forms
from django.utils.translation import gettext_lazy as _
from ckeditor.widgets import CKEditorWidget

from .models import Post, Comment, Tag, Section, PostType

class PostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(), label=_('Зміст'))
    new_tags = forms.CharField(required=False, label=_('Нові теги'),
                              help_text=_('Введіть нові теги через кому'))
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'section', 'tags', 'post_type']
        labels = {
            'title': _('Заголовок'),
            'section': _('Розділ'),
            'tags': _('Теги'),
            'post_type': _('Тип посту'),
        }
        widgets = {
            'tags': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].queryset = Tag.objects.all().order_by('name')
        self.fields['section'].queryset = Section.objects.filter(is_active=True).order_by('title')
        self.fields['post_type'].queryset = PostType.objects.all()
    
    def save(self, commit=True):
        post = super().save(commit=False)
        
        if commit:
            post.save()
            self.save_m2m()
            
            # Process new tags
            new_tags_str = self.cleaned_data.get('new_tags', '')
            if new_tags_str:
                tag_names = [name.strip() for name in new_tags_str.split(',') if name.strip()]
                for tag_name in tag_names:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    post.tags.add(tag)
        
        return post

class CommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), label=_('Коментар'))
    
    class Meta:
        model = Comment
        fields = ['content']

class SearchForm(forms.Form):
    q = forms.CharField(required=False, label=_('Пошук'), 
                       widget=forms.TextInput(attrs={'placeholder': _('Пошук за словами...')}))
    tag = forms.CharField(required=False, label=_('Тег'),
                         widget=forms.TextInput(attrs={'placeholder': _('Пошук за тегом...')}))
