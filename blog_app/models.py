from re import I
from statistics import mode
import uuid
from django.db import models
from youonline_social_app.constants import s3_compress_image, create_slug
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from PIL import Image
import sys
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.storage import default_storage as storage
import random, string
from moviepy.editor import VideoFileClip
from django.conf import settings
import time
from youonline_social_app.models import Profile, Language
from youonline_social_app.models import Post
from youonline_social_app.constants import *


YOUONLINE_PRIVACY_CHOICES = [
        ('Public', 'Public'),
        ('OnlyMe', 'OnlyMe'),
        ('Friends', 'Friends'),
    ]
class BlogCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return str(self.title)

    class Meta:
        db_table = 'BlogCategory'
    
class Blog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    # Foreign Keys
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, null=True, blank=True)
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True)
    post=models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    description = models.TextField(null=True, blank=True)
    posted_date = models.DateField(null=True, blank=True)
    view_count = models.BigIntegerField(default=0)
    shared_count = models.BigIntegerField(null=True, blank=True)
    is_promoted = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_compressed = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # Create slug for blog title
        if not self.slug:
            slugs = list(Blog.objects.all().values_list('slug', flat=True))
            self.slug = create_slug(title=self.title, slugs=slugs)
        super(Blog, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.title)

    class Meta:
        db_table = 'Blog'

class BlogMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True, blank=True, related_name='blogmedia_blog')
    # Media
    featured_image = models.ImageField(upload_to='Blogs/%Y/%m', max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)

    def __str__(self):
        return str(self.blog.title)

    def save(self, *args, **kwargs):
        if self.featured_image and not self.is_compressed:
            self.featured_image = s3_compress_image(self.featured_image)
            self.is_compressed = True
        super(BlogMedia, self).save(*args, **kwargs)


    class Meta:
        db_table = 'BlogMedia'


class BlogTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    tags=models.CharField(max_length=500, null=True, blank=True)
    blog=models.ForeignKey(Blog, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.tags

    class Meta:
        db_table='BlogTag'


class BlogWatched(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="blogwatched_profile")
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True, blank=True, related_name="blogwatched_blog")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.blog)

    class Meta:
        db_table = 'BlogWatched'


class BlogAuthor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="blogauthor_profile")

    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True, default='')
    description = models.TextField(null=True, blank=True)
    resume = models.FileField(upload_to='Blog/Resume/%Y/%m',null=True, blank=True)
    language = models.ForeignKey('youonline_social_app.Language', on_delete=models.CASCADE, null=True, blank=True)
    country = models.ForeignKey('youonline_social_app.Country', on_delete=models.CASCADE, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    bucket_uploaded = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'BlogAuthor'