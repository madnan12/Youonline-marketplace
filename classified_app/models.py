from unicodedata import category
import uuid
from django.db import models
from youonline_social_app.constants import generate_video_thumbnail, s3_compress_image, create_slug
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
from job_app.models import *
from property_app.models import *
from automotive_app.models import *
from youonline_social_app.models import *
import tempfile


YOUONLINE_PRIVACY_CHOICES = [
        ('Public', 'Public'),
        ('OnlyMe', 'OnlyMe'),
        ('Friends', 'Friends'),
    ]

# Create your models here.

class ClassifiedCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255)
    image = models.ImageField(max_length=255, upload_to='classified_category_images', null=True, blank=True)
    background_color = models.TextField(null=True, blank=True)
    view_count = models.BigIntegerField(default=0)
    
    business_directory = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'ClassifiedCategory'

    def __str__(self):
        return str(self.title)

class ClassifiedSubCategory(models.Model):
    category = models.ForeignKey(ClassifiedCategory, related_name='classified_sub_category', on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    image = models.ImageField(max_length=255, upload_to='classified_subcategory_images', null=True, blank=True)

    background_color = models.TextField(null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'ClassifiedSubCategory'

    def is_business_directory(self):
        try:
            return self.category.business_directory
        except:
            return False


    def __str__(self):
        return str(self.title)


class ClassifiedeMake(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=64)
    image = models.ImageField(max_length=256, upload_to='classified_make_images', null=True, blank=True)
    subcategory = models.ForeignKey(ClassifiedSubCategory, on_delete=models.CASCADE, null=True, blank=True, related_name="classifiedmake_subcategory")
    background_color = models.TextField(null=True, blank=True)

    is_featured = models.BooleanField(default=False)
    class Meta:
        db_table = 'ClassifiedeMake'

    def __str__(self):
        return str(self.title)


class ClassifiedSubSubCategory(models.Model):
    sub_category = models.ForeignKey(ClassifiedSubCategory, related_name='classified_sub_sub_category', on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255)

    image = models.ImageField(max_length=256, upload_to='classified_subsub_images', null=True, blank=True)
    background_color = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'ClassifiedSubSubCategory'

    def __str__(self):
        return str(self.id)


class Classified(models.Model):
    DURATION_CHOICES = [
        ('7 days', '7 days'),
        ('14 days', '14 days'),
        ('30 days', '30 days'),
    ]
    TYPE_CHOICES = [
        ('Used', 'Used'),
        ('New', 'New'),
    ]
    VERIFICATION_STATUS = [
        ('Pending', 'Pending'),
        ('Verified', 'Verified'),
        ('Rejected', 'Rejected'),
    ]
    
    BUSINESS_CHOICES = [
        ('Individual', 'Individual'),
        ('Company', 'Company'),
    ]

    category = models.ForeignKey(ClassifiedCategory, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(ClassifiedSubCategory, on_delete=models.CASCADE, null=True, blank=True)
    sub_sub_category = models.ForeignKey(ClassifiedSubSubCategory, on_delete=models.CASCADE, null=True, blank=True)
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey('youonline_social_app.Post', on_delete=models.CASCADE, null=True, blank=True, related_name='post_classified')
    company = models.ForeignKey('job_app.Company', on_delete=models.CASCADE, null=True, blank=True)
    make = models.ForeignKey(ClassifiedeMake, on_delete=models.CASCADE, null=True, blank=True, related_name="classified_classifiedmake")


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    country = models.ForeignKey('youonline_social_app.Country', on_delete=models.CASCADE, null=True, blank=True)
    state = models.ForeignKey('youonline_social_app.State', on_delete=models.CASCADE, null=True, blank=True)
    city = models.ForeignKey('youonline_social_app.City', on_delete=models.CASCADE, null=True, blank=True)
    language = models.ForeignKey('youonline_social_app.Language', on_delete=models.CASCADE, null=True, blank=True)
    dial_code = models.CharField(max_length=255, null=True, blank=True)

    # Location
    street_adress = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)

    mobile = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True, choices=TYPE_CHOICES)
    business_type = models.CharField(max_length=255, choices=BUSINESS_CHOICES, null=True, blank=True)

    # Pricing
    currency = models.ForeignKey('job_app.Currency', on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    deal_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    description = models.TextField(null=True, blank=True)

    business_directory = models.BooleanField(default=False)
    established_year = models.CharField(max_length=255 , default='' , null=True , blank=True)
    employees_count = models.CharField(max_length=255 , default='' , null=True , blank=True)
    manager_name = models.CharField(max_length=255 , default='' , null=True , blank=True)

    quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    duration = models.CharField(max_length=255, choices=DURATION_CHOICES, null=True, blank=True)
    privacy = models.CharField(max_length=255, choices=YOUONLINE_PRIVACY_CHOICES, null=True, blank=True)
    verification_status = models.CharField(max_length=255, choices=VERIFICATION_STATUS, default='Pending', null=True, blank=True)
    view_count = models.BigIntegerField(default=0)

    long = models.DecimalField(max_digits=30, decimal_places=16, null=True, blank=True)
    lat = models.DecimalField(max_digits=30, decimal_places=16,  null=True, blank=True)
    
    is_deleted = models.BooleanField(default=False)
    is_active =  models.BooleanField(default=True)
    is_promoted = models.BooleanField(default=False)
    is_deal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            slugs = list(Classified.objects.all().values_list('slug', flat=True))
            self.slug = create_slug(name=self.name, slugs=slugs)
        super(Classified, self).save(*args, **kwargs)

    def get_sub_category_name(self):
        try:
            return f'{self.sub_category.title}'
        except:
            return 'N/A'

    class Meta:
        db_table = 'Classified'

    def __str__(self):
        return str(self.name)


class ClassifiedMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey('youonline_social_app.Post', on_delete=models.CASCADE, null=True, blank=True, related_name='classifiedmedia_post')
    classified = models.ForeignKey(Classified, on_delete=models.CASCADE, null=True, blank=True, related_name='classifiedmedia_classified')
    # Media
    classified_image = models.ImageField(max_length=256, upload_to='classified_images/%Y/%m', null=True, blank=True)
    classified_video = models.FileField(max_length=256, upload_to='classified_video/%Y/%m', null=True, blank=True)
    classified_video_thumbnail = models.FileField(max_length=256, upload_to='classified_video_thumbnail/%Y/%m', null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_compressed = models.BooleanField(default=False)
    video_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.classified)

    def save(self, *args, **kwargs):
        if self.classified_image and not self.is_compressed:
            self.classified_image = s3_compress_image(self.classified_image)
            self.is_compressed = True
        # Generate Video Thumnail
        if self.classified_video and not self.classified_video_thumbnail:
            # Get Temporary File Path
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_path = temp_file.name
            with open(temp_path, 'wb+') as destination:
                 for chunk in self.classified_video.chunks():
                           destination.write(chunk)
            # Instantiate VideoFileClip object
            clip = VideoFileClip(temp_path)
            # Get video frame at 1 second
            temp_thumb = clip.get_frame(1)
            # Convert numpy array to pillow image and compress it
            self.classified_video_thumbnail = generate_video_thumbnail(temp_thumb)
        super(ClassifiedMedia, self).save(*args, **kwargs)
        # if self.classified_video:
        #     clip = VideoFileClip(self.classified_video.path)
        #     # resizing video downsize 50 %
        #     compressed_vid = clip.resize(0.5)
        #     compressed_vid.write_videofile(self.classified_video.path)


    class Meta:
        db_table = 'ClassifiedMedia'


# class ClassifiedView(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
#     classified = models.ForeignKey(Classified, on_delete=models.CASCADE, related_name="classifiedview_classified")
#     viewer = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, related_name="classifiedview_viewer", null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

#     class Meta:
#         db_table = 'ClassifiedView'

#     def __str__(self):
#         return f"{self.classified.name} viewed by {self.viewer.user.username}"

class ContactClassified(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True)
    classified = models.ForeignKey(Classified, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.classified)

    class Meta:
        db_table = 'ContactClassified'


class ReportClassified(models.Model):
    REPORT_CHOICES = [
        ('Fraud', 'Fraud'),
        ('Offensive content', 'Offensive content'),
        ('Duplicate ad', 'Duplicate ad'),
        ('Product alread sold', 'Product alread sold'),
        ('Other', 'Other'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True)
    classified = models.ForeignKey(Classified, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    report_type = models.CharField(max_length=255, choices=REPORT_CHOICES, default='Other', null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.classified)

    class Meta:
        db_table = 'ReportClassified'


class FavouriteClassified(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True, related_name="favouriteclassified_profile")
    classified = models.ForeignKey(Classified, on_delete=models.CASCADE, null=True, blank=True, related_name="favouriteclassified_classified")
    is_deleted = models.BooleanField(default=False)
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.classified)

    class Meta:
        db_table = 'FavouriteClassified'
        unique_together = ('profile', 'classified')

class ClassifiedSearchHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True, related_name="classifiedsearchhistory_profile")
    classified = models.ForeignKey(Classified, on_delete=models.CASCADE, null=True, blank=True, related_name="classifiedsearchhistory_classfied")
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.classified.id)
        
    class Meta:
        db_table = 'ClassifiedSearchHistory'
