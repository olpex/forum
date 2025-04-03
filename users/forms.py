from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.utils.translation import gettext_lazy as _

from .models import User

class UserLoginForm(forms.Form):
    email = forms.EmailField(label=_('Email адреса'), widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label=_('Пароль'), widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label=_('Ім\'я'), max_length=30, required=True, 
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label=_('Прізвище'), max_length=30, required=True, 
                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label=_('Email адреса'), max_length=254, required=True, 
                           widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['username'].help_text = _('Необхідний. 150 символів або менше. Літери, цифри та @/./+/-/_.')
        self.fields['password1'].help_text = _('Ваш пароль повинен містити щонайменше 8 символів.')
        self.fields['password2'].help_text = _('Введіть той самий пароль для перевірки.')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UserBanForm(forms.Form):
    BAN_CHOICES = [
        (0, _('Назавжди')),
        (7, _('1 тиждень')),
        (14, _('2 тижні')),
        (21, _('3 тижні')),
        (30, _('1 місяць')),
        (90, _('3 місяці')),
        (180, _('6 місяців')),
        (365, _('1 рік')),
    ]
    
    ban_days = forms.ChoiceField(label=_('Тривалість блокування'), choices=BAN_CHOICES, 
                               widget=forms.Select(attrs={'class': 'form-control'}))
    reason = forms.CharField(label=_('Причина блокування'), widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), 
                           required=False)
    
    def clean_ban_days(self):
        return int(self.cleaned_data['ban_days'])

class AdminUserCreateForm(UserCreationForm):
    ROLE_CHOICES = [
        (User.ADMIN, _('Адміністратор')),
        (User.STUDENT, _('Студент')),
    ]
    
    role = forms.ChoiceField(label=_('Роль'), choices=ROLE_CHOICES, 
                           widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'role', 'password1', 'password2')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['username'].help_text = _('Необхідний. 150 символів або менше. Літери, цифри та @/./+/-/_.')
        self.fields['password1'].help_text = _('Ваш пароль повинен містити щонайменше 8 символів.')
        self.fields['password2'].help_text = _('Введіть той самий пароль для перевірки.')
