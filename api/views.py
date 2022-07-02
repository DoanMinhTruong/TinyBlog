import json
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics, mixins , permissions
from rest_framework.views import status
# Create your views here.
from .serializers import PostCategorySerializer, PostTagSerializer, TagSerializer, UserSerializer
from .models import PostCategory, PostTag, Tag, User
from django.core import serializers
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken

class UserView(mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    def get(self, request, *args, **kwargs):
        users = User.objects.filter(is_superuser = False).values("id" , "username","email", "full_name","gender", "image" , "intro")
        return Response(users)
    def post(self , request,  *args, **kwargs):
        return self.create(request, *args, **kwargs)
    def put(self, request, *args , **kwargs):
        try:
            user =  request.user.id
            data_user = request.data
            if(user != data_user['id']):
                return Response({
                    "message" : "You dont have any permissions"
                } , status = status.HTTP_400_BAD_REQUEST)
            if('password' in data_user):
                data_user['password'] = make_password(data_user['password'])
            serializer = self.serializer_class(User.objects.get(id = user), data = data_user, partial = True)
            
            if(serializer.is_valid()):
            
                instance = serializer.save()
                refresh = RefreshToken.for_user(instance)
                return Response({
                    "refresh" : str(refresh),
                    "access" : str(refresh.access_token),
                    "updated" : serializer.data,
                })
            return Response({"message" : "Update fail"})
        except:
            return Response(status = status.HTTP_400_BAD_REQUEST)
    def delete(self, request, *args , **kwargs):
        try:
            user = request.user.id
            if(user != request.data['id']):
                return Response({
                    "message" : "You dont have any permissions"
                }, status = status.HTTP_400_BAD_REQUEST)
            get = User.objects.get(id = user)
            get.delete()
            return Response({
                "message" : "Delete Success"
            } , status = status.HTTP_200_OK)
        except:
            return Response(status = status.HTTP_400_BAD_REQUEST)



class UserDetailView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id = request.data['id'])
            response = json.dumps(user)
            del response['password'], response['is_active'] ,response['is_superuser'] , response['is_staff']
            return Response(response, status = status.HTTP_200_OK)
        except:
            return Response(status = status.HTTP_400_BAD_REQUEST)
    def post(self, request, *args, **kwargs):
        try:   
            user = User.objects.get(id = request.data['id'])
            response = json.dumps(user)
            if(user.id != request.data['id']):
                del response['password'], response['is_active'] ,response['is_superuser'] , response['is_staff']
            return Response(response , status = status.HTTP_200_OK)   
        except:
            return Response(status = status.HTTP_400_BAD_REQUEST)


from .models import Post
from .serializers import PostSerializer
from django.utils.text import slugify
from django.utils.crypto import get_random_string
class PostView(generics.GenericAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    def get(self, request , *args , **kwargs):
        print(request.data)
        if('author_id' in request.data) and ('id' in request.data):
            posts = Post.objects.filter(
                author_id = request.data['author_id'],
                id = request.data['id']
            )
            if(request.user.id == request.data['author_id']):
                return Response(posts.values())
            return Response(posts.filter(published = True).values())
        if('author_id' in request.data):
            posts = Post.objects.filter(
                author_id = request.data['author_id']
            )
            if(request.user.id == request.data['author_id']):
                return Response(posts.values())
            return Response(posts.filter(published = True).values())
        if('id' in request.data):
            post = Post.objects.filter(id = request.data['id'])
            if(request.user.id == post.first().author_id):
                return Response(post.values())
            return Response(post.filter(published = True).values())        
        if(request.user.is_superuser):
            return Response(Post.objects.all())
        return Response(Post.objects.filter(published = True).values() )
    def post(self, request, *args, **kwargs):
        author = request.user
        if(author.is_superuser):
            return Response({
                "message" : "Admin can not create any posts"
            } , status = status.HTTP_400_BAD_REQUEST)
        data = {}
        data.update(request.data)
        data['author'] = author.id
        slug = slugify(data['title'])
        data['slug'] = slug
        while(Post.objects.filter(slug = data['slug']).exists()):
            data['slug'] = slug + get_random_string(length = 4)

        serializer = self.serializer_class(data = data)
        if(serializer.is_valid()):
            serializer.save()
            return Response({
                "created" : serializer.data
            } , status = status.HTTP_201_CREATED)
        return Response({
            "message" : serializer.errors
        } , status = status.HTTP_400_BAD_REQUEST)
    def put(self, request, *args , **kwargs):
        print(request.user)
        if(request.user.id != request.data['author_id'] and not request.user.is_superuser):
            return Response({
                "message" : "You dont have any permissions"
            }, status = status.HTTP_401_UNAUTHORIZED)
        serializer = self.serializer_class(Post.objects.get(id = request.data['id']) , data = request.data , partial = True)
        if(serializer.is_valid()):
            serializer.save()
            return Response({
                "updated" : serializer.data
            }, status = status.HTTP_200_OK)
        return Response({
            "message" : serializer.errors
        }, status = status.HTTP_400_BAD_REQUEST)
    def delete(self, request , *args , **kwargs):
        post = Post.objects.get(id = request.data['id'])
        if(post.author_id != request.user.id and not request.user.is_superuser):
            return Response({
                "message" : "You dont have any permissions"
            } , status = status.HTTP_401_UNAUTHORIZED)
        post.delete()
        return Response({
            "message" : "Delete Success"
        })


from .models import PostComment
from .serializers import PostCommentSerializer
class PostCommentView(generics.GenericAPIView):
    serializer_class = PostCommentSerializer
    queryset = PostComment.objects.all()

    def get(self, request, *args , **kwargs):
        try:
            if('post_id' in request.data):
                return Response(PostComment.objects.filter(post_id = request.data['post_id']).values())
            return Response(PostComment.objects.all().values())
        except:
            return Response(status = status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        # try:
            post = Post.objects.get(id = request.data['post_id'])
            if(post.published):
                data = {
                    'post' : post.id,
                    'content' : request.data['content'],
                }
                data['author'] = request.user.id
                print(data)
                serializer = self.serializer_class(data = data, partial = True)
                if(serializer.is_valid()):
                    serializer.save()
                    return Response({
                        "created" : serializer.data
                    } , status = status.HTTP_200_OK)
                return Response({
                    "message" : serializer.errors
                }, status = status.HTTP_400_BAD_REQUEST)
            # return Response(status = status.HTTP_400_BAD_REQUEST)
            
        # except Exception:
        #     return Response(status = status.HTTP_400_BAD_REQUEST)
    def delete(self, request, *args, **kwargs):
        try:
            post_cmt = PostComment.objects.get(id = request.data['id'])
            if(post_cmt.author_id == request.user.id):
                post_cmt.delete()
                return Response({
                    "message" : "Delete Success",
                } , status = status.HTTP_200_OK)
            return Response({
                "message" : "Delete Fail"
            } , status = status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status = status.HTTP_400_BAD_REQUEST)


from .models import Category
from .serializers import CategorySerializer

class CategoryView( generics.ListCreateAPIView , generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [permissions.IsAdminUser]

class PostCategoryView(generics.GenericAPIView):
    serializer_class = PostCategorySerializer
    queryset = PostCategory.objects.all()

    def get(self , request, *args ,**kwargs):
        try:
            post = Post.objects.get(id = request.data['post_id'])
            if(not post.published):
                if(post.author_id != request.user.id and not request.user.is_superuser):
                    return Response({
                        "message" : "You dont have any permissions" ,  
                    } , status = status.HTTP_400_BAD_REQUEST)
                
            response = {'post_id' : request.data['post_id'] , 'category' : []}
            list_post_cate = PostCategory.objects.filter(post_id = request.data['post_id']).values()
            for i in list_post_cate:
                response['category'].append(i['category_id'])
            return Response(response , status = status.HTTP_200_OK)

        except:
            return Response(status = status.HTTP_400_BAD_REQUEST)

    def post(self, request , *args, **kwargs):
        try:
            post = Post.objects.get(id = request.data['post_id'])
            if(post.author_id != request.user.id):
                return Response({
                    "message" : "You dont have any permissions" 
                } , status = status.HTTP_400_BAD_REQUEST)
            lst_cate = request.data['category']
            check = []
            for cate in lst_cate:
                data = {}
                data['post_id'] = request.data['post_id']
                data['category_id'] = cate
                serializer = self.serializer_class(data = data , partial = True)
                if(serializer.is_valid()):
                    check.append(serializer)
                else:
                    return Response({
                        "message" : serializer.errors
                    }, status = status.HTTP_400_BAD_REQUEST)
            created = {"created" : []}
            for ser in check:
                ser.save()
                created['created'].append(ser.data)

            return Response(created, status = status.HTTP_201_CREATED)
        except:
            return Response(status = status.HTTP_400_BAD_REQUEST)
    
class TagView(mixins.ListModelMixin , generics.GenericAPIView):
    serializer_class = TagSerializer
    def post(self, request , *args, **kwargs):
        try:
            if(not request.user.is_authenticated):
                return Response({
                    "message" : "You dont have any permissions"
                }, status = status.HTTP_400_BAD_REQUEST)
            tags = Tag.objects.filter(name = request.data['name'])
            if(tags.exists()):
                return Response({"message" : "This tag already exists"} , status = status.HTTP_200_OK)
            serializer = self.serializer_class(data = request.data, partial = True)
            if(serializer.is_valid()):
                serializer.save()
                return Response({
                    "created" : serializer.data
                } , status = status.HTTP_201_CREATED)
            return Response({'message' : serializer.errors} , status = status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status = status.HTTP_400_BAD_REQUEST)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args , **kwargs)


class PostTagView(generics.GenericAPIView):
    serializer_class = PostTagSerializer
    def post(self, request , *args ,**kwargs):
        post = Post.objects.get(id = request.data['id'])
        if(post.author_id != request.user.id):
            return Response({"message" : "You dont have any permissions"} , status = status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data = request.data , partial = True)
        if(serializer.is_valid()):
            serializer.save()
            return Response({
                    "created" : serializer.data
                } , status = status.HTTP_201_CREATED)
        return Response({'message' : serializer.errors} , status = status.HTTP_400_BAD_REQUEST)
    def delete(self, request, *args , **kwargs):
        post_tag = PostTag.objects.get(id = request.data['id'])
        post = Post.objects.get(id = post_tag.post_id)
        if(request.user.id != post.author_id and not request.user.is_superuser):
            return Response({"message" : "You dont have any permissions"} , status = status.HTTP_400_BAD_REQUEST)
        post_tag.delete()        
        return Response({'message' : 'Delete Success'} , status = status.HTTP_200_OK)