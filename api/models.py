from distutils.command.upload import upload
from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager

# Create your models here.


class MyUserManager(BaseUserManager):
    def create_user(self, username , email , password = None, **extra_fields):

        if not username:
            raise ValueError("User must have an username")
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have an password")
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using = self._db)
        return user
    def create_superuser(self, username , email, password ,**extra_fields):
        user = self.create_user(username,  email , password  , **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using = self._db)
        return user

class User(AbstractBaseUser):
    username = models.CharField(name='username' , max_length=255 , unique = True)
    email = models.EmailField('email address' , unique=True)
    
    full_name = models.CharField(max_length=255, blank= True)
    gender = models.CharField(verbose_name='gender', max_length=1, default='U', choices =(
        ('M' , 'Male'),
        ('F' , 'Female'),
        ('U' , 'Others')
    ) )
    created_at = models.DateTimeField(auto_now_add=True)

    image = models.ImageField(upload_to = 'image/' , default = 'image/download.jpg')
    intro = models.TextField(blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)


    USERNAME_FIELD = 'username' 
    REQUIRED_FIELDS = ['email']

    objects = MyUserManager()

    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj=None):
        return self.is_active and self.is_superuser
    def has_module_perms(self, app_label):
        return self.is_active and self.is_superuser
        
class Post(models.Model):
    author = models.ForeignKey(User , on_delete=models.CASCADE)
    title = models.CharField(verbose_name="post title" , blank=False , null = False , max_length=255 )
    slug = models.SlugField(max_length=255 , unique=True)
    summary = models.TextField()
    published = models.BooleanField(blank = False, null = False , default = True)
    created_at = models.DateTimeField(auto_now_add= True)
    update_at = models.DateTimeField(auto_now = True)
    content = models.TextField(null=False, blank=False)
    def __str__(self):
        return self.title
class PostComment(models.Model):
    post = models.ForeignKey(Post , on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add= True)
    content = models.TextField(null=False, blank=False)
    def __str__(self) :
        return ("(Author: " + str(self.author) + "-> Post: " + str(self.post) + "): " +  str(self.content))
class Tag(models.Model):
    name = models.CharField(verbose_name="tag name" , max_length=200 , null=False, blank=False)
    content = models.TextField()
class PostTag(models.Model):
    post = models.ForeignKey(Post , on_delete= models.DO_NOTHING)
    tag = models.ForeignKey(Tag, on_delete= models.DO_NOTHING)

class Category(models.Model):
    name = models.CharField(verbose_name="category name" , max_length=200 , null = False, blank=False)
    content = models.TextField()
class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.DO_NOTHING)
    category = models.ForeignKey(Category , on_delete=models.DO_NOTHING)
    