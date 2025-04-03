from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Admin panel
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/users/', views.admin_user_list, name='admin_user_list'),
    path('admin-panel/users/<int:pk>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin-panel/users/<int:pk>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin-panel/users/<int:pk>/ban/', views.admin_user_ban, name='admin_user_ban'),
    path('admin-panel/users/<int:pk>/unban/', views.admin_user_unban, name='admin_user_unban'),
    path('admin-panel/users/<int:pk>/freeze/', views.admin_user_freeze, name='admin_user_freeze'),
    path('admin-panel/users/<int:pk>/unfreeze/', views.admin_user_unfreeze, name='admin_user_unfreeze'),
    path('admin-panel/users/<int:pk>/delete/', views.admin_user_delete, name='admin_user_delete'),
    
    # Section management
    path('admin-panel/sections/', views.admin_section_list, name='admin_section_list'),
    path('admin-panel/sections/new/', views.admin_section_create, name='admin_section_create'),
    path('admin-panel/sections/<int:pk>/edit/', views.admin_section_edit, name='admin_section_edit'),
    path('admin-panel/sections/<int:pk>/freeze/', views.admin_section_freeze, name='admin_section_freeze'),
    path('admin-panel/sections/<int:pk>/unfreeze/', views.admin_section_unfreeze, name='admin_section_unfreeze'),
    path('admin-panel/sections/<int:pk>/delete/', views.admin_section_delete, name='admin_section_delete'),
    
    # Content management
    path('admin-panel/posts/', views.admin_post_list, name='admin_post_list'),
    path('admin-panel/posts/<int:pk>/freeze/', views.admin_post_freeze, name='admin_post_freeze'),
    path('admin-panel/posts/<int:pk>/unfreeze/', views.admin_post_unfreeze, name='admin_post_unfreeze'),
    path('admin-panel/posts/<int:pk>/delete/', views.admin_post_delete, name='admin_post_delete'),
    path('admin-panel/comments/', views.admin_comment_list, name='admin_comment_list'),
    path('admin-panel/comments/<int:pk>/freeze/', views.admin_comment_freeze, name='admin_comment_freeze'),
    path('admin-panel/comments/<int:pk>/unfreeze/', views.admin_comment_unfreeze, name='admin_comment_unfreeze'),
    path('admin-panel/comments/<int:pk>/delete/', views.admin_comment_delete, name='admin_comment_delete'),
]
