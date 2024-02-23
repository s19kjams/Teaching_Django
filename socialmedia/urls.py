"""
URL configuration for socialmedia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from SocialHub import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup', views.create_profile, name='create_profile'),
    path('dashboard', views.DashboardView.as_view(), name='dashboard'),
    path('login', views.LoginView.as_view(), name='login'),


    path('create_post/<str:username>', views.create_post, name='create_post'),
    path('read_post/<int:post_id>', views.read_post, name='read_post'),
    path('update_post/<str:username>/<int:post_number>', views.update_post, name='update_post'),
    path('delete_post', views.delete_post, name='delete_post'),

    path('create_comment/<str:username_who_published_post>/<int:post_number>', views.create_comment,
         name='create_comment'),
    path('read_comments/<str:username_who_published_post>/<int:post_number>', views.read_comments,
         name='read_comments'),
    path('update_comment/<int:comment_id>', views.update_comment, name='update_comment'),
    path('delete_comment/<int:comment_id>', views.delete_comment, name='delete_comment'),

    path('like_post/<int:post_id>', views.like_post, name='like_post'),

    path('follow_unfollow_user/<str:targeted_username>', views.follow_unfollow_user, name='follow_unfollow_user'),

    path('read_profile/<str:targeted_username>', views.read_profile, name='read_profile'),
]