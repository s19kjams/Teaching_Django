from django import forms
from .models import Profile, Post, Comment


class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    bio = forms.CharField(max_length=500, required=False)

    class Meta:
        model = Profile
        fields = ['username', 'first_name', 'last_name', 'email', 'password']


class UserLoginForm(forms.ModelForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Profile
        fields = ['username', 'password']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']


class DeletePostForm(forms.Form):
    username = forms.CharField()
    post_number = forms.IntegerField()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']