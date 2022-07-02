from django.urls import path , include


from .views import  CategoryView, PostCategoryView, TagView, PostTagView, UserView, UserDetailView , PostView , PostCommentView
from rest_framework_simplejwt import views,serializers


class MyTokenObtainPairSerializer(serializers.TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['id'] = self.user.id
        return data
class MyTokenObtainPairView(views.TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    


user_urlpatterns = [
    path('' , UserView.as_view() , name = "User Control View"),
    path('detail/' , UserDetailView.as_view() , name = "User Detail View") ,
    path('login/' , MyTokenObtainPairView.as_view() , name = "Login View"),
    path('refresh/', views.TokenRefreshView.as_view() , name = "Token Refresh"),
]

post_urlpatterns = [
    path('' , PostView.as_view() , name = "Post View") ,
]
comment_urlpatterns = [
    path('' , PostCommentView.as_view() , name = "Post Comment View")
]


urlpatterns = [
    path('user/' , include(user_urlpatterns)),
    path('post/' , include(post_urlpatterns)),
    path('comment/' , include(comment_urlpatterns)),
    path('category/' , CategoryView.as_view() , name = "Category View"),
    path('postcategory/' , PostCategoryView.as_view() , name = "Post Category View"),
    path('tag/' , TagView.as_view() , name = "Tag View"),
    path('posttag/' , PostTagView.as_view() , name = "Post Tag View"),
]
