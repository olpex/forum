from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Home page and section views
    path('', views.home, name='home'),
    path('sections/', views.section_list, name='section_list'),
    path('sections/<int:pk>/', views.section_detail, name='section_detail'),
    
    # Post views
    path('posts/new/', views.post_create, name='post_create'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:pk>/close/', views.post_close, name='post_close'),
    path('posts/<int:pk>/reopen/', views.post_reopen, name='post_reopen'),
    path('posts/<int:pk>/freeze/', views.post_freeze, name='post_freeze'),
    path('posts/<int:pk>/unfreeze/', views.post_unfreeze, name='post_unfreeze'),
    path('posts/<int:pk>/delete/', views.post_delete, name='post_delete'),
    
    # Comment views
    path('posts/<int:post_pk>/comment/', views.comment_create, name='comment_create'),
    path('comments/<int:pk>/edit/', views.comment_edit, name='comment_edit'),
    path('comments/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    path('comments/<int:pk>/freeze/', views.comment_freeze, name='comment_freeze'),
    path('comments/<int:pk>/unfreeze/', views.comment_unfreeze, name='comment_unfreeze'),
    path('comments/<int:pk>/reply/', views.comment_reply, name='comment_reply'),
    
    # Voting
    path('posts/<int:pk>/upvote/', views.post_upvote, name='post_upvote'),
    path('posts/<int:pk>/downvote/', views.post_downvote, name='post_downvote'),
    path('posts/<int:pk>/remove-vote/', views.post_remove_vote, name='post_remove_vote'),
    path('comments/<int:pk>/upvote/', views.comment_upvote, name='comment_upvote'),
    path('comments/<int:pk>/downvote/', views.comment_downvote, name='comment_downvote'),
    path('comments/<int:pk>/remove-vote/', views.comment_remove_vote, name='comment_remove_vote'),
    
    # Tag views
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/<str:tag_name>/', views.tag_posts, name='tag_posts'),
    
    # Search
    path('search/', views.search, name='search'),
    
    # Archive
    path('archive/', views.archive, name='archive'),
    path('archive/<int:year>/<int:month>/', views.archive_month, name='archive_month'),
]
