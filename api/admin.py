from django.contrib import admin
from .models import PostCategory, PostTag, Tag, User, Post , PostComment, Category
# Register your models here.
admin.site.register([User , Post , PostComment , Category, PostCategory, Tag , PostTag])