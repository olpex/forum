from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.db.models import Q

from .models import User, UserAction
from .forms import UserLoginForm, UserRegistrationForm, UserProfileForm, UserBanForm
from core.models import Section, Post, Comment

def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                if user.is_banned:
                    if user.ban_until and user.ban_until < timezone.now():
                        # Ban period is over, unban the user
                        user.unban()
                        login(request, user)
                        messages.success(request, _('Вітаємо на форумі!'))
                        return redirect('core:home')
                    else:
                        ban_message = _('Ваш обліковий запис заблоковано.')
                        if user.ban_until:
                            ban_message += _(' Блокування діє до {0}.').format(user.ban_until.strftime('%d.%m.%Y %H:%M'))
                        if user.ban_reason:
                            ban_message += _(' Причина: {0}').format(user.ban_reason)
                        messages.error(request, ban_message)
                elif user.is_frozen:
                    messages.error(request, _('Ваш обліковий запис заморожено. Зверніться до адміністратора.'))
                else:
                    login(request, user)
                    messages.success(request, _('Вітаємо на форумі!'))
                    return redirect('core:home')
            else:
                messages.error(request, _('Невірна електронна пошта або пароль.'))
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})

def signup(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.STUDENT  # Default role for self-registration
            user.save()
            
            # Log in the user after registration
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=user.email, password=raw_password)
            login(request, user)
            
            messages.success(request, _('Реєстрація успішна! Вітаємо на форумі!'))
            return redirect('core:home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/signup.html', {'form': form})

@login_required
def profile(request):
    """User profile view"""
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    user_comments = Comment.objects.filter(author=request.user).order_by('-created_at')
    
    return render(request, 'users/profile.html', {
        'user': request.user,
        'posts': user_posts,
        'comments': user_comments,
    })

@login_required
def profile_edit(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Профіль успішно оновлено!'))
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'users/profile_edit.html', {'form': form})

# Admin panel views
@login_required
def admin_panel(request):
    """Admin panel home"""
    if not (request.user.is_superadmin() or request.user.is_admin()):
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    # Stats for superadmin
    if request.user.is_superadmin():
        total_users = User.objects.count()
        total_admins = User.objects.filter(role=User.ADMIN).count()
        total_students = User.objects.filter(role=User.STUDENT).count()
        total_sections = Section.objects.count()
        total_posts = Post.objects.count()
        total_comments = Comment.objects.count()
        
        context = {
            'total_users': total_users,
            'total_admins': total_admins,
            'total_students': total_students,
            'total_sections': total_sections,
            'total_posts': total_posts,
            'total_comments': total_comments,
        }
    # Stats for admin
    else:
        admin_sections = Section.objects.filter(created_by=request.user).count()
        section_ids = Section.objects.filter(created_by=request.user).values_list('id', flat=True)
        admin_posts = Post.objects.filter(section__id__in=section_ids).count()
        admin_comments = Comment.objects.filter(post__section__id__in=section_ids).count()
        
        context = {
            'admin_sections': admin_sections,
            'admin_posts': admin_posts,
            'admin_comments': admin_comments,
        }
    
    return render(request, 'users/admin_panel.html', context)

@login_required
def admin_user_list(request):
    """List users for admin management"""
    if not (request.user.is_superadmin() or request.user.is_admin()):
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    
    # Base queryset
    if request.user.is_superadmin():
        users = User.objects.all()
    else:
        # Admins can only see students
        users = User.objects.filter(role=User.STUDENT)
    
    # Apply filters
    if query:
        users = users.filter(
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    
    if role_filter:
        users = users.filter(role=role_filter)
    
    if status_filter == 'active':
        users = users.filter(is_active=True, is_frozen=False, is_banned=False)
    elif status_filter == 'frozen':
        users = users.filter(is_frozen=True)
    elif status_filter == 'banned':
        users = users.filter(is_banned=True)
    
    return render(request, 'users/admin_user_list.html', {
        'users': users,
        'query': query,
        'role_filter': role_filter,
        'status_filter': status_filter,
    })

@login_required
def admin_user_detail(request, pk):
    """View user details"""
    if not (request.user.is_superadmin() or request.user.is_admin()):
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    user = get_object_or_404(User, pk=pk)
    
    # Admins can only view students
    if request.user.is_admin() and user.role != User.STUDENT:
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    user_actions = UserAction.objects.filter(user=user).order_by('-timestamp')
    user_posts = Post.objects.filter(author=user).order_by('-created_at')
    user_comments = Comment.objects.filter(author=user).order_by('-created_at')
    
    return render(request, 'users/admin_user_detail.html', {
        'user_profile': user,
        'user_actions': user_actions,
        'posts': user_posts,
        'comments': user_comments,
    })

@login_required
def admin_user_ban(request, pk):
    """Ban a user"""
    if not (request.user.is_superadmin() or request.user.is_admin()):
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    user = get_object_or_404(User, pk=pk)
    
    # Admins can only ban students
    if request.user.is_admin() and user.role != User.STUDENT:
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    # Superadmins cannot be banned
    if user.is_superadmin():
        messages.error(request, _('Суперадміністратора не можна заблокувати.'))
        return redirect('users:admin_user_detail', pk=user.pk)
    
    if request.method == 'POST':
        form = UserBanForm(request.POST)
        if form.is_valid():
            ban_days = form.cleaned_data.get('ban_days')
            reason = form.cleaned_data.get('reason')
            
            user.ban(reason=reason, days=ban_days if ban_days > 0 else None)
            
            # Create action record
            UserAction.objects.create(
                user=user,
                actor=request.user,
                action=UserAction.ACTION_BAN,
                reason=reason
            )
            
            messages.success(request, _('Користувача заблоковано.'))
            return redirect('users:admin_user_detail', pk=user.pk)
    else:
        form = UserBanForm()
    
    return render(request, 'users/admin_user_ban.html', {
        'form': form,
        'user_profile': user,
    })

@login_required
def admin_user_unban(request, pk):
    """Unban a user"""
    if not (request.user.is_superadmin() or request.user.is_admin()):
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    user = get_object_or_404(User, pk=pk)
    
    # Admins can only unban students
    if request.user.is_admin() and user.role != User.STUDENT:
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    if not user.is_banned:
        messages.error(request, _('Цей користувач не заблокований.'))
        return redirect('users:admin_user_detail', pk=user.pk)
    
    user.unban()
    
    # Create action record
    UserAction.objects.create(
        user=user,
        actor=request.user,
        action=UserAction.ACTION_UNBAN
    )
    
    messages.success(request, _('Користувача розблоковано.'))
    return redirect('users:admin_user_detail', pk=user.pk)

@login_required
def admin_user_freeze(request, pk):
    """Freeze a user account"""
    if not (request.user.is_superadmin() or request.user.is_admin()):
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    user = get_object_or_404(User, pk=pk)
    
    # Admins can only freeze students
    if request.user.is_admin() and user.role != User.STUDENT:
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    # Superadmins cannot be frozen
    if user.is_superadmin():
        messages.error(request, _('Суперадміністратора не можна заморозити.'))
        return redirect('users:admin_user_detail', pk=user.pk)
    
    if user.is_frozen:
        messages.error(request, _('Цей користувач вже заморожений.'))
        return redirect('users:admin_user_detail', pk=user.pk)
    
    reason = request.POST.get('reason', '')
    
    user.freeze()
    
    # Create action record
    UserAction.objects.create(
        user=user,
        actor=request.user,
        action=UserAction.ACTION_FREEZE,
        reason=reason
    )
    
    messages.success(request, _('Користувача заморожено.'))
    return redirect('users:admin_user_detail', pk=user.pk)

@login_required
def admin_user_unfreeze(request, pk):
    """Unfreeze a user account"""
    if not (request.user.is_superadmin() or request.user.is_admin()):
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    user = get_object_or_404(User, pk=pk)
    
    # Admins can only unfreeze students
    if request.user.is_admin() and user.role != User.STUDENT:
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    if not user.is_frozen:
        messages.error(request, _('Цей користувач не заморожений.'))
        return redirect('users:admin_user_detail', pk=user.pk)
    
    user.unfreeze()
    
    # Create action record
    UserAction.objects.create(
        user=user,
        actor=request.user,
        action=UserAction.ACTION_UNFREEZE
    )
    
    messages.success(request, _('Користувача розморожено.'))
    return redirect('users:admin_user_detail', pk=user.pk)

@login_required
def admin_user_delete(request, pk):
    """Delete a user account"""
    if not request.user.is_superadmin():
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    user = get_object_or_404(User, pk=pk)
    
    # Superadmins cannot be deleted
    if user.is_superadmin():
        messages.error(request, _('Суперадміністратора не можна видалити.'))
        return redirect('users:admin_user_detail', pk=user.pk)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        # Create action record before deleting
        UserAction.objects.create(
            user=user,
            actor=request.user,
            action=UserAction.ACTION_DELETE,
            reason=reason
        )
        
        # Delete the user
        user.delete()
        
        messages.success(request, _('Користувача видалено.'))
        return redirect('users:admin_user_list')
    
    return render(request, 'users/admin_user_delete.html', {
        'user_profile': user,
    })

# Section management views for admin panel
@login_required
def admin_section_list(request):
    """List sections for admin management"""
    if not (request.user.is_superadmin() or request.user.is_admin()):
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    if request.user.is_superadmin():
        sections = Section.objects.all()
    else:
        sections = Section.objects.filter(created_by=request.user)
    
    return render(request, 'users/admin_section_list.html', {
        'sections': sections,
    })

@login_required
def admin_section_create(request):
    """Create a new section"""
    if not (request.user.is_superadmin() or request.user.is_admin()):
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        if title:
            section = Section.objects.create(
                title=title,
                description=description,
                created_by=request.user
            )
            
            messages.success(request, _('Розділ успішно створено!'))
            return redirect('users:admin_section_list')
        else:
            messages.error(request, _('Назва розділу не може бути порожньою.'))
    
    return render(request, 'users/admin_section_create.html')

@login_required
def admin_section_edit(request, pk):
    """Edit a section"""
    if not (request.user.is_superadmin() or request.user.is_admin()):
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    section = get_object_or_404(Section, pk=pk)
    
    # Admins can only edit their own sections
    if request.user.is_admin() and section.created_by != request.user:
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        if title:
            section.title = title
            section.description = description
            section.save()
            
            messages.success(request, _('Розділ успішно оновлено!'))
            return redirect('users:admin_section_list')
        else:
            messages.error(request, _('Назва розділу не може бути порожньою.'))
    
    return render(request, 'users/admin_section_edit.html', {
        'section': section,
    })

@login_required
def admin_section_freeze(request, pk):
    """Freeze a section"""
    if not (request.user.is_superadmin() or request.user.is_admin()):
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    section = get_object_or_404(Section, pk=pk)
    
    # Admins can only freeze their own sections
    if request.user.is_admin() and section.created_by != request.user:
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    section.freeze()
    messages.success(request, _('Розділ заморожено.'))
    return redirect('users:admin_section_list')

@login_required
def admin_section_unfreeze(request, pk):
    """Unfreeze a section"""
    if not (request.user.is_superadmin() or request.user.is_admin()):
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    section = get_object_or_404(Section, pk=pk)
    
    # Admins can only unfreeze their own sections
    if request.user.is_admin() and section.created_by != request.user:
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    section.unfreeze()
    messages.success(request, _('Розділ розморожено.'))
    return redirect('users:admin_section_list')

@login_required
def admin_section_delete(request, pk):
    """Delete a section"""
    if not request.user.is_superadmin():
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    section = get_object_or_404(Section, pk=pk)
    
    if request.method == 'POST':
        section.delete()
        messages.success(request, _('Розділ видалено.'))
        return redirect('users:admin_section_list')
    
    return render(request, 'users/admin_section_delete.html', {
        'section': section,
    })

# Content management views for admin panel
@login_required
def admin_post_list(request):
    """List posts for admin management"""
    if not (request.user.is_superadmin() or request.user.is_admin()):
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    if request.user.is_superadmin():
        posts = Post.objects.all().order_by('-created_at')
    else:
        # Admins can only manage posts in their sections
        section_ids = Section.objects.filter(created_by=request.user).values_list('id', flat=True)
        posts = Post.objects.filter(section__id__in=section_ids).order_by('-created_at')
    
    return render(request, 'users/admin_post_list.html', {
        'posts': posts,
    })

@login_required
def admin_post_freeze(request, pk):
    """Freeze a post"""
    if not (request.user.is_superadmin() or request.user.is_admin()):
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    post = get_object_or_404(Post, pk=pk)
    
    # Admins can only freeze posts in their sections
    if request.user.is_admin() and post.section.created_by != request.user:
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    post.freeze()
    messages.success(request, _('Пост заморожено.'))
    return redirect('users:admin_post_list')

@login_required
def admin_post_unfreeze(request, pk):
    """Unfreeze a post"""
    if not (request.user.is_superadmin() or request.user.is_admin()):
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    post = get_object_or_404(Post, pk=pk)
    
    # Admins can only unfreeze posts in their sections
    if request.user.is_admin() and post.section.created_by != request.user:
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    post.unfreeze()
    messages.success(request, _('Пост розморожено.'))
    return redirect('users:admin_post_list')

@login_required
def admin_post_delete(request, pk):
    """Delete a post"""
    if not (request.user.is_superadmin() or request.user.is_admin()):
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    post = get_object_or_404(Post, pk=pk)
    
    # Admins can only delete posts in their sections
    if request.user.is_admin() and post.section.created_by != request.user:
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    # Admins can't delete other admins' posts
    if request.user.is_admin() and post.author.is_admin() and post.author != request.user:
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        post.delete()
        messages.success(request, _('Пост видалено.'))
        return redirect('users:admin_post_list')
    
    return render(request, 'users/admin_post_delete.html', {
        'post': post,
    })

@login_required
def admin_comment_list(request):
    """List comments for admin management"""
    if not (request.user.is_superadmin() or request.user.is_admin()):
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    if request.user.is_superadmin():
        comments = Comment.objects.all().order_by('-created_at')
    else:
        # Admins can only manage comments in their sections
        section_ids = Section.objects.filter(created_by=request.user).values_list('id', flat=True)
        comments = Comment.objects.filter(post__section__id__in=section_ids).order_by('-created_at')
    
    return render(request, 'users/admin_comment_list.html', {
        'comments': comments,
    })

@login_required
def admin_comment_freeze(request, pk):
    """Freeze a comment"""
    if not (request.user.is_superadmin() or request.user.is_admin()):
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    comment = get_object_or_404(Comment, pk=pk)
    
    # Admins can only freeze comments in their sections
    if request.user.is_admin() and comment.post.section.created_by != request.user:
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    comment.freeze()
    messages.success(request, _('Коментар заморожено.'))
    return redirect('users:admin_comment_list')

@login_required
def admin_comment_unfreeze(request, pk):
    """Unfreeze a comment"""
    if not (request.user.is_superadmin() or request.user.is_admin()):
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    comment = get_object_or_404(Comment, pk=pk)
    
    # Admins can only unfreeze comments in their sections
    if request.user.is_admin() and comment.post.section.created_by != request.user:
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    comment.unfreeze()
    messages.success(request, _('Коментар розморожено.'))
    return redirect('users:admin_comment_list')

@login_required
def admin_comment_delete(request, pk):
    """Delete a comment"""
    if not (request.user.is_superadmin() or request.user.is_admin()):
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    comment = get_object_or_404(Comment, pk=pk)
    
    # Admins can only delete comments in their sections
    if request.user.is_admin() and comment.post.section.created_by != request.user:
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    # Admins can't delete other admins' comments
    if request.user.is_admin() and comment.author.is_admin() and comment.author != request.user:
        return HttpResponseForbidden(_('Доступ заборонено'))
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        comment.delete()
        messages.success(request, _('Коментар видалено.'))
        return redirect('users:admin_comment_list')
    
    return render(request, 'users/admin_comment_delete.html', {
        'comment': comment,
    })
