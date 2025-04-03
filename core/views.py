from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse

from .models import Section, Tag, Post, Comment, PostType, ActionLog
from .forms import PostForm, CommentForm, SearchForm

def home(request):
    """Home page with latest posts and sections"""
    sections = Section.objects.filter(is_active=True)
    recent_posts = Post.objects.filter(is_frozen=False).order_by('-created_at')[:10]
    popular_tags = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    
    # Archive data for sidebar
    archive_dates = Post.objects.dates('created_at', 'month', order='DESC')
    
    return render(request, 'core/home.html', {
        'sections': sections,
        'recent_posts': recent_posts,
        'popular_tags': popular_tags,
        'archive_dates': archive_dates,
    })

def section_list(request):
    """List all active sections"""
    sections = Section.objects.filter(is_active=True)
    return render(request, 'core/section_list.html', {'sections': sections})

def section_detail(request, pk):
    """Show a section and its posts"""
    section = get_object_or_404(Section, pk=pk, is_active=True)
    posts = Post.objects.filter(section=section).order_by('-created_at')
    
    return render(request, 'core/section_detail.html', {
        'section': section,
        'posts': posts,
    })

@login_required
def post_create(request):
    """Create a new post"""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            
            # Handle tags
            form.save_m2m()  # Save the many-to-many data for the form
            
            # Log the action
            ActionLog.objects.create(
                user=request.user,
                action=ActionLog.ACTION_CREATE,
                content_type=ActionLog.CONTENT_POST,
                content_id=post.id
            )
            
            messages.success(request, _('Пост успішно створено!'))
            return redirect('core:post_detail', pk=post.pk)
    else:
        form = PostForm()
    
    return render(request, 'core/post_form.html', {'form': form})

def post_detail(request, pk):
    """Show a post and its comments"""
    post = get_object_or_404(Post, pk=pk)
    comments = Comment.objects.filter(post=post, parent=None).order_by('created_at')
    
    # Comment form for logged in users
    comment_form = None
    if request.user.is_authenticated and not post.is_closed and not post.is_frozen:
        comment_form = CommentForm()
    
    return render(request, 'core/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    })

@login_required
def post_edit(request, pk):
    """Edit a post"""
    post = get_object_or_404(Post, pk=pk)
    
    # Check if user is authorized to edit
    if post.author != request.user and not request.user.is_superadmin() and not (request.user.is_admin() and post.section.created_by == request.user):
        messages.error(request, _('Ви не маєте прав на редагування цього посту.'))
        return redirect('core:post_detail', pk=post.pk)
    
    if post.is_frozen:
        messages.error(request, _('Цей пост заморожено і не може бути відредаговано.'))
        return redirect('core:post_detail', pk=post.pk)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            
            # Log the action
            ActionLog.objects.create(
                user=request.user,
                action=ActionLog.ACTION_UPDATE,
                content_type=ActionLog.CONTENT_POST,
                content_id=post.id
            )
            
            messages.success(request, _('Пост успішно оновлено!'))
            return redirect('core:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'core/post_form.html', {'form': form, 'post': post})

@login_required
def post_close(request, pk):
    """Close a post to prevent new comments"""
    post = get_object_or_404(Post, pk=pk)
    
    # Check if user is authorized to close
    if post.author != request.user and not request.user.is_superadmin() and not (request.user.is_admin() and post.section.created_by == request.user):
        messages.error(request, _('Ви не маєте прав на закриття цього посту.'))
        return redirect('core:post_detail', pk=post.pk)
    
    post.close()
    
    # Log the action
    ActionLog.objects.create(
        user=request.user,
        action=ActionLog.ACTION_CLOSE,
        content_type=ActionLog.CONTENT_POST,
        content_id=post.id
    )
    
    messages.success(request, _('Пост успішно закрито!'))
    return redirect('core:post_detail', pk=post.pk)

@login_required
def post_reopen(request, pk):
    """Reopen a closed post"""
    post = get_object_or_404(Post, pk=pk)
    
    # Check if user is authorized to reopen
    if post.author != request.user and not request.user.is_superadmin() and not (request.user.is_admin() and post.section.created_by == request.user):
        messages.error(request, _('Ви не маєте прав на відкриття цього посту.'))
        return redirect('core:post_detail', pk=post.pk)
    
    post.reopen()
    
    # Log the action
    ActionLog.objects.create(
        user=request.user,
        action=ActionLog.ACTION_REOPEN,
        content_type=ActionLog.CONTENT_POST,
        content_id=post.id
    )
    
    messages.success(request, _('Пост успішно відкрито!'))
    return redirect('core:post_detail', pk=post.pk)

@login_required
def comment_create(request, post_pk):
    """Create a new comment on a post"""
    post = get_object_or_404(Post, pk=post_pk)
    
    if post.is_closed:
        messages.error(request, _('Цей пост закрито і не приймає нових коментарів.'))
        return redirect('core:post_detail', pk=post.pk)
    
    if post.is_frozen:
        messages.error(request, _('Цей пост заморожено і не приймає нових коментарів.'))
        return redirect('core:post_detail', pk=post.pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            
            # Log the action
            ActionLog.objects.create(
                user=request.user,
                action=ActionLog.ACTION_CREATE,
                content_type=ActionLog.CONTENT_COMMENT,
                content_id=comment.id
            )
            
            messages.success(request, _('Коментар успішно додано!'))
            return redirect('core:post_detail', pk=post.pk)
    else:
        form = CommentForm()
    
    return render(request, 'core/comment_form.html', {
        'form': form,
        'post': post,
    })

@login_required
def comment_reply(request, pk):
    """Reply to a comment"""
    parent_comment = get_object_or_404(Comment, pk=pk)
    post = parent_comment.post
    
    if post.is_closed:
        messages.error(request, _('Цей пост закрито і не приймає нових коментарів.'))
        return redirect('core:post_detail', pk=post.pk)
    
    if post.is_frozen:
        messages.error(request, _('Цей пост заморожено і не приймає нових коментарів.'))
        return redirect('core:post_detail', pk=post.pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.parent = parent_comment
            comment.save()
            
            # Log the action
            ActionLog.objects.create(
                user=request.user,
                action=ActionLog.ACTION_CREATE,
                content_type=ActionLog.CONTENT_COMMENT,
                content_id=comment.id
            )
            
            messages.success(request, _('Відповідь успішно додано!'))
            return redirect('core:post_detail', pk=post.pk)
    else:
        form = CommentForm()
    
    return render(request, 'core/comment_form.html', {
        'form': form,
        'post': post,
        'parent_comment': parent_comment,
    })

def tag_list(request):
    """List all tags"""
    tags = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')
    return render(request, 'core/tag_list.html', {'tags': tags})

def tag_posts(request, tag_name):
    """Show posts with a specific tag"""
    tag = get_object_or_404(Tag, name=tag_name)
    posts = Post.objects.filter(tags=tag).order_by('-created_at')
    
    return render(request, 'core/tag_posts.html', {
        'tag': tag,
        'posts': posts,
    })

def search(request):
    """Search posts by keywords and tags"""
    query = request.GET.get('q', '')
    tag_query = request.GET.get('tag', '')
    
    posts = Post.objects.all()
    
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query)
        )
    
    if tag_query:
        posts = posts.filter(tags__name=tag_query)
    
    popular_tags = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    
    return render(request, 'core/search_results.html', {
        'posts': posts,
        'query': query,
        'tag_query': tag_query,
        'popular_tags': popular_tags,
    })

def archive(request):
    """Show archive of posts by date"""
    dates = Post.objects.dates('created_at', 'month', order='DESC')
    return render(request, 'core/archive.html', {'dates': dates})

def archive_month(request, year, month):
    """Show posts from a specific month"""
    start_date = timezone.datetime(year, month, 1)
    if month == 12:
        end_date = timezone.datetime(year + 1, 1, 1)
    else:
        end_date = timezone.datetime(year, month + 1, 1)
    
    posts = Post.objects.filter(
        created_at__gte=start_date,
        created_at__lt=end_date
    ).order_by('-created_at')
    
    return render(request, 'core/archive_month.html', {
        'posts': posts,
        'year': year,
        'month': month,
    })

# AJAX voting views
@login_required
def post_upvote(request, pk):
    """Upvote a post"""
    post = get_object_or_404(Post, pk=pk)
    post.upvote(request.user)
    return JsonResponse({'score': post.vote_score})

@login_required
def post_downvote(request, pk):
    """Downvote a post"""
    post = get_object_or_404(Post, pk=pk)
    post.downvote(request.user)
    return JsonResponse({'score': post.vote_score})

@login_required
def post_remove_vote(request, pk):
    """Remove vote from a post"""
    post = get_object_or_404(Post, pk=pk)
    post.remove_vote(request.user)
    return JsonResponse({'score': post.vote_score})

@login_required
def comment_upvote(request, pk):
    """Upvote a comment"""
    comment = get_object_or_404(Comment, pk=pk)
    comment.upvote(request.user)
    return JsonResponse({'score': comment.vote_score})

@login_required
def comment_downvote(request, pk):
    """Downvote a comment"""
    comment = get_object_or_404(Comment, pk=pk)
    comment.downvote(request.user)
    return JsonResponse({'score': comment.vote_score})

@login_required
def comment_remove_vote(request, pk):
    """Remove vote from a comment"""
    comment = get_object_or_404(Comment, pk=pk)
    comment.remove_vote(request.user)
    return JsonResponse({'score': comment.vote_score})
