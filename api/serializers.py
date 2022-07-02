from dataclasses import field, fields
from rest_framework import serializers
from .models import Category, PostCategory, PostComment, PostTag, Tag, User , Post

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username' ,'password', 'email' , 'full_name' , 'gender' , 'created_at' , 'intro' , 'image')
        extra_kwargs = {"password": {"write_only": True}}
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance



class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id' , 'author' , 'title' , 'slug' , 'summary' , 'published' , 'content')

class PostCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostComment
        fields = ('id' , 'post' , 'author', 'content') 

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class PostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCategory
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class PostTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostTag
        fields = '__all__'