import threading

from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .forms import UserRegistrationForm, UserLoginForm, PostForm, DeletePostForm, CommentForm
from .models import Profile, Post, Comment, Like, Follow
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse, HttpResponseBadRequest
import logging

logger = logging.getLogger("logger")


def log_message_async(level, message):
    if level == "info":
        logger.info(message)
    elif level == "error":
        logger.error(message)


def get_post_from_user(username, post_number):
    user_who_published_post = User.objects.get(username=username)
    post = Post.objects.filter(user=user_who_published_post).order_by('id')[post_number - 1]
    return post


def create_profile(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                )
                profile = Profile(user=user, bio=form.cleaned_data['bio'])

                message = f'Profile with username {user.username} has just been created!'

                logging_thread = threading.Thread(target=log_message_async, args=("info", message,))
                logging_thread.start()

                profile.save()

            except Exception as e:
                logger.error(e)
            return redirect('/login')
    elif request.method == 'GET':
        form = UserRegistrationForm()
    return render(request, 'SocialHub/create_profile.html', {'form': form})


class LoginView(APIView):
    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            try:
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(username=username, password=password)
                if user is not None:
                    profile = Profile.objects.get(user=user)
                    profile.is_logged_in = True
                    profile.save()

                    message = f"Profile with username {username} has just logged in"

                    logging_thread = threading.Thread(target=log_message_async, args=("info", message,))
                    logging_thread.start()

                    refresh = RefreshToken.for_user(user)

                    return JsonResponse({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    })
            except Exception as e:
                logging_thread = threading.Thread(target=log_message_async, args=("error", str(e),))
                logging_thread.start()

                return redirect('/login')

            else:
                return redirect('/login')

    def get(self, request):
        form = UserLoginForm()
        return render(request, 'SocialHub/login.html', {'form': form})


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return render(request, 'SocialHub/dashboard.html')


def create_post(request, username):
    if request.method == 'GET':
        form = PostForm()
        return render(request, 'SocialHub/create_post.html', {'form': form})
    else:
        user = User.objects.get(username=username)
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = user
            post.save()

            message = f'Post with id {post.id} created!'

            logging_thread = threading.Thread(target=log_message_async, args=("info", message,))
            logging_thread.start()

            return redirect('/dashboard')


def read_post(request, post_id):
    post = Post.objects.get(id=post_id)
    number_of_likes = Like.objects.filter(post=post).count()
    return render(request, 'SocialHub/read_post.html', {'post': post,
                                                        'number_of_likes': number_of_likes})


def update_post(request, username, post_number):
    post = get_post_from_user(username, post_number)

    if request.method == 'GET':
        form = PostForm(instance=post)
        return render(request, 'SocialHub/update_post.html', {'form': form})
    else:
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()

            message = f'Post with id {post.id} has just been updated!'
            logging_thread = threading.Thread(target=log_message_async, args=("info", message,))
            logging_thread.start()

            return redirect('/dashboard')


def delete_post(request):
    if request.method == 'GET':
        form = DeletePostForm()
        return render(request, 'SocialHub/delete_post.html', {'form': form})
    else:
        form = DeletePostForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            post_number = form.cleaned_data['post_number']

            user = User.objects.get(username=username)
            posts = Post.objects.filter(user=user).order_by('created_at')

            try:
                post = posts[post_number - 1]
            except IndexError as ie:
                logging_thread = threading.Thread(target=log_message_async, args=("err", str(ie),))
                logging_thread.start()

                return render(request, 'SocialHub/delete_post.html',
                              {'form': form, 'error': 'Post does not exist'})

            message = f"Post {post.id} deleted successfully"

            logging_thread = threading.Thread(target=log_message_async, args=("info", message,))
            logging_thread.start()

            post.delete()

            return redirect('/dashboard')


def create_comment(request, username_who_published_post, post_number):
    if request.method == 'POST':
        post = get_post_from_user(username_who_published_post, post_number)

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()

            message = f"Username with id {request.user.id} has just commented for post with id {post.id}"
            logging_thread = threading.Thread(target=log_message_async, args=("info", message,))
            logging_thread.start()

            return redirect('/dashboard')

    else:
        form = CommentForm()
        return render(request, 'SocialHub/create_comment.html', {'form': form})


def read_comments(request, username_who_published_post, post_number):
    post = get_post_from_user(username_who_published_post, post_number)
    comments = Comment.objects.filter(post=post)
    return render(request, 'SocialHub/read_comments.html', {'comments': comments, 'post_number': post_number,
                                                            'username': username_who_published_post})


def update_comment(request, comment_id):
    comment = Comment.objects.get(id=comment_id)

    if comment.user != request.user:
        return HttpResponseBadRequest("You are not authorized!")

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)

        if form.is_valid():
            form.save()

            message = f"Username with id {request.user.id} has just updated his comment for comment with id {comment.id}"
            logging_thread = threading.Thread(target=log_message_async, args=("info", message,))
            logging_thread.start()

            return redirect('/dashboard')
    else:
        form = CommentForm(instance=comment)
        return render(request, 'SocialHub/update_comment.html', {'form': form})


def delete_comment(request, comment_id):
    comment = Comment.objects.get(id=comment_id)

    if comment.user != request.user:
        return HttpResponseBadRequest("You are not authorized!")

    comment.delete()

    message = f"Username with id {request.user.id} has just deleted his comment for comment with id {comment_id}"
    logging_thread = threading.Thread(target=log_message_async, args=("info", message,))
    logging_thread.start()

    return redirect('/dashboard')


def like_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    message = ""
    if not created:
        like.delete()
        message = f"Username with id {request.user.id} has just unliked post with id {post_id}"
    else:
        message = f"Username with id {request.user.id} has just liked post with id {post_id}"

    logging_thread = threading.Thread(target=log_message_async, args=("info", message,))
    logging_thread.start()

    return redirect(f"/read_post/{post_id}")


def is_following(follower, followed_user):
    return Follow.objects.filter(follower=follower, followed_user=followed_user).exists()


def follow_unfollow_user(request, targeted_username):
    target_user = get_object_or_404(User, username=targeted_username)
    message = ""
    if is_following(request.user, target_user):
        Follow.objects.get(follower=request.user, followed_user=target_user).delete()
        message = f"Username with id {request.user.id} has just unfollowed username {target_user.username}"

    else:
        Follow.objects.create(follower=request.user, followed_user=target_user)
        message = f"Username with id {request.user.id} has just followed username {target_user.username}"

    logging_thread = threading.Thread(target=log_message_async, args=("info", message,))
    logging_thread.start()

    return redirect(f"/read_profile/{targeted_username}")


def read_profile(request, targeted_username):
    target_user = get_object_or_404(User, username=targeted_username)
    target_profile = get_object_or_404(Profile, user=target_user)

    follower_number = Follow.objects.filter(followed_user=target_user).count()
    following_number = Follow.objects.filter(follower=target_user).count()

    is_following_already = is_following(request.user, target_user)
    follow_unfollow_button = "Unfollow" if is_following_already else "Follow"

    return render(request, 'SocialHub/read_profile.html', {'profile': target_profile,
                                                           'followers': follower_number,
                                                           'followings': following_number,
                                                           'follow_unfollow_button': follow_unfollow_button})
