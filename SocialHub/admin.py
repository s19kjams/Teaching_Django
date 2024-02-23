from django.contrib import admin

from SocialHub.models import Post, Profile, Comment, Like, Follow

# Register your models here.
admin.site.register(Post)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Follow)