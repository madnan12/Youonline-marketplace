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
from job_app.models import *
import tempfile

# colors
# ['F2FCE4','FFF8D1','ECFFEC','FEEFEA','FFF3EB','FFF3FF','F2FCE4','F2FCE4',
# 'FFF8D1','ECFFEC','FEEFEA','FFF3EB','FFF3FF','F2FCE4','F2FCE4','FFF8D1',
# 'ECFFEC','FEEFEA','FFF3EB','FFF3FF','F2FCE4']


YOUONLINE_PRIVACY_CHOICES = [
        ('Public', 'Public'),
        ('OnlyMe', 'OnlyMe'),
        ('Friends', 'Friends'),
    ]

# Create your models here.
class AutomotiveCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=64)

    image = models.ImageField(max_length=255, upload_to='automotive_category_images', null=True, blank=True)
    background_color = models.TextField(null=True, blank=True)
    view_count = models.BigIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'AutomotiveCategory'

    def __str__(self):
        return str(self.title)


class AutomotiveSubCategory(models.Model):
    category = models.ForeignKey(AutomotiveCategory, related_name='automotive_sub_category', on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=64)
    image = models.ImageField(max_length=255, upload_to='automotive_subcategory_images',  null=True, blank=True)
    background_color = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'AutomotiveSubCategory'

    def __str__(self):
        return str(self.title)


class AutomotiveSubSubCategory(models.Model):
    sub_category = models.ForeignKey(AutomotiveSubCategory, related_name='automotive_sub_sub_category', on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=64)
    image = models.ImageField(max_length=255, upload_to='automotive_subsubcategory_images', null=True, blank=True)
    background_color = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'AutomotiveSubSubCategory'

    def __str__(self):
        return str(self.title)


class AutomotiveMake(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=64)
    image = models.ImageField(max_length=256, upload_to='automotive_make_images', null=True, blank=True)
    sub_category = models.ForeignKey(AutomotiveSubCategory, on_delete=models.CASCADE, null=True, blank=True, related_name="automotivemake_subcategory")
    background_color = models.TextField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    class Meta:
        db_table = 'AutomotiveMake'

    def __str__(self):
        return str(self.title)


class AutomotiveModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    brand = models.ForeignKey(AutomotiveMake, on_delete=models.CASCADE, null=True, blank=True, related_name="atuomotivemodel_automotivemake")
    title = models.CharField(max_length=64)
    image = models.ImageField(max_length=255, upload_to='automotivemodel_images', null=True, blank=True)
    background_color = models.TextField(null=True, blank=True)
    year = models.CharField(max_length=16, null=True, blank=True)
    
    class Meta:
        db_table = 'AutomotiveModel'

    def __str__(self):
        return str(self.title)


class Automotive(models.Model):
    CAR_TYPE_CHOICES = [
        ('New', 'New'),
        ('Used', 'Used'),
    ]
    BODY_CONDITION_CHOICES = [
        ('Perfect Inside and Outside', 'Perfect Inside and Outside'),
        ('No accidents, very few faults', 'No accidents, very few faults'),
        ('Bit of wear tear, all repaired', 'Bit of wear tear, all repaired'),
        ('Lots of wear tear to the body', 'Lots of wear tear to the body'),
    ]
    INSIDE_OUT_CHOICES = [
        ('Perfect Inside and Outside', 'Perfect Inside and Outside'),
        ('Minor faults, all fixed', 'Minor faults, all fixed'),
        ('Major faults fixed, small remains', 'Major faults fixed, small remains'),
        ('Ongoing minor major faults', 'Ongoing minor major faults'),
    ]
    TRANSMISSION_TYPE_CHOICES = [
        ('Manual', 'Manual'),
        ('Automatic', 'Automatic'),
    ]
    FUEL_TYPE_CHOICES = [
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('LPG', 'LPG'),
        ('CNG', 'CNG'),
        ('Hybrid', 'Hybrid'),
        ('Electric', 'Electric'),
    ]
    DOOR_CHOICES = [
        ('2 doors', '2 doors'),
        ('3 doors', '3 doors'),
        ('4 doors', '4 doors'),
        ('5+ doors', '5+ doors'),
    ]
    SPECS_CHOICES = [
        ('European Specs', 'European Specs'),
        ('GCC Specs', 'GCC Specs'),
        ('Japanese Specs', 'Japanese Specs'),
        ('North American Specs', 'North American Specs'),
        ('Other', 'Other'),
    ]
    POWER_CHOICES = [
        ('Less than 150 HP', 'Less than 150 HP'),
        ('150- 200 HP', '150- 200 HP'),
        ('200- 300 HP', '200- 300 HP'),
        ('300- 400 HP', '300- 400 HP'),
        ('400- 500 HP', '400- 500 HP'),
        ('Other', 'Other')
    ]
    VERIFICATION_STATUS = [
        ('Pending', 'Pending'),
        ('Verified', 'Verified'),
        ('Rejected', 'Rejected'),
    ]

    AUTOMOTIVE_INSPECTION_CHOICES = [
        ('Courtesy Inspection','Courtesy Inspection'),
        ('Insurance Inspection','Insurance Inspection'),
        ('12Point Inspection','12 Point Inspection'),
    ]

    BUSINESS_CHOICES = [
        ('Individual', 'Individual'),
        ('Company', 'Company'),
    ]

    category = models.ForeignKey(AutomotiveCategory, on_delete=models.CASCADE, related_name="automotive_category")
    sub_category = models.ForeignKey(AutomotiveSubCategory, on_delete=models.CASCADE, null=True, blank=True, related_name="automotive_subcategory")
    sub_sub_category = models.ForeignKey(AutomotiveSubSubCategory, on_delete=models.CASCADE, null=True, blank=True, related_name="automotive_subsubcategory")
    make = models.ForeignKey(AutomotiveMake, on_delete=models.CASCADE, null=True, blank=True, related_name="atuomotive_automotivemake")
    automotive_model = models.ForeignKey(AutomotiveModel, on_delete=models.CASCADE, null=True, blank=True, related_name="automotive_atuomotivemodel")
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True, related_name="automotive_profile")
    post = models.ForeignKey('youonline_social_app.Post', on_delete=models.CASCADE, null=True, blank=True, related_name='post_automotive')
    company = models.ForeignKey('job_app.Company', on_delete=models.CASCADE, null=True, blank=True, related_name="automotive_company")
    company_name = models.CharField(max_length=512, null=True, blank=True)
    company_license = models.CharField(max_length=512, null=True, blank=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    country = models.ForeignKey('youonline_social_app.Country', on_delete=models.CASCADE, null=True, blank=True, related_name="automotive_country")
    state = models.ForeignKey('youonline_social_app.State', on_delete=models.CASCADE, null=True, blank=True, related_name="automotive_state")
    city = models.ForeignKey('youonline_social_app.City', on_delete=models.CASCADE, null=True, blank=True, related_name="automotive_city")
    language = models.ForeignKey('youonline_social_app.Language', on_delete=models.CASCADE, null=True, blank=True, related_name="automotive_language")

    # Location
    street_adress = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)

    mobile = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    # Pricing
    currency = models.ForeignKey('job_app.Currency', on_delete=models.CASCADE, null=True, blank=True, related_name="automotive_currency")
    price = models.DecimalField(max_digits=12, decimal_places=2)

    description = models.TextField(null=True, blank=True)

    car_type = models.CharField(max_length=255, null=True, blank=True, choices=CAR_TYPE_CHOICES)
    quantity = models.BigIntegerField(null=True, blank=True)
    kilometers = models.BigIntegerField(null=True, blank=True)
    body_condition = models.CharField(max_length=255, null=True, blank=True, choices=BODY_CONDITION_CHOICES)
    inside_out = models.CharField(max_length=255, null=True, blank=True, choices=INSIDE_OUT_CHOICES)
    transmission_type = models.CharField(max_length=255, null=True, blank=True, choices=TRANSMISSION_TYPE_CHOICES)
    dial_code = models.CharField(max_length=255, null=True, blank=True)

    specs = models.CharField(max_length=255, null=True, blank=True, choices=SPECS_CHOICES)
    door = models.CharField(max_length=255, null=True, blank=True, choices=DOOR_CHOICES)
    power = models.CharField(max_length=255, null=True, blank=True, choices=POWER_CHOICES)
    fuel_type = models.CharField(max_length=255, null=True, blank=True, choices=FUEL_TYPE_CHOICES)

    year = models.CharField(max_length=255, null=True, blank=True)
    color = models.CharField(max_length=255, null=True, blank=True)
    warranty = models.BooleanField(default=False)
    privacy = models.CharField(max_length=255, choices=YOUONLINE_PRIVACY_CHOICES, null=True, blank=True)

    automotive_inspection = models.CharField(max_length=255, choices=AUTOMOTIVE_INSPECTION_CHOICES, null=True, blank=True)
    automotive_year = models.BigIntegerField(null=True, blank=True)

    verification_status = models.CharField(max_length=255, choices=VERIFICATION_STATUS, default='Pending', null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_deal = models.BooleanField(default=False)
    view_count = models.BigIntegerField(default=0)

    long = models.DecimalField(max_digits=30, decimal_places=16, null=True, blank=True)
    lat = models.DecimalField(max_digits=30, decimal_places=16,  null=True, blank=True)
    
    is_active =  models.BooleanField(default=True)
    is_promoted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    business_type = models.CharField(max_length=255, choices=BUSINESS_CHOICES, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            slugs = list(Automotive.objects.all().values_list('slug', flat=True))
            self.slug = create_slug(name=self.name, slugs=slugs)
        super(Automotive, self).save(*args, **kwargs)

    class Meta:
        db_table = 'Automotive'

    def __str__(self):
        return str(self.name)


class AutomotiveMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True, related_name='automotivemedia_profile')
    post = models.ForeignKey('youonline_social_app.Post', on_delete=models.CASCADE, null=True, blank=True, related_name='automotivemedia_post')
    automotive = models.ForeignKey(Automotive, on_delete=models.CASCADE, null=True, blank=True, related_name='automotivemedia_automotive')
    # Media
    automotive_image = models.ImageField(max_length=256, upload_to='automotive_images/%Y/%m', null=True, blank=True)
    automotive_video = models.FileField(max_length=256, upload_to='automotive_video/%Y/%m', null=True, blank=True)
    vid_thumbnail = models.FileField(max_length=256, upload_to='automotive_video/%Y/%m', null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_compressed = models.BooleanField(default=False)
    video_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)

    def __str__(self):
        return str(self.automotive)

    def save(self, *args, **kwargs):
        if self.automotive_image and not self.is_compressed:
            self.automotive_image = s3_compress_image(self.automotive_image)
            self.is_compressed = True
        # Generate Video Thumnail
        if self.automotive_video and not self.vid_thumbnail:
            # Get Temporary File Path
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_path = temp_file.name
            with open(temp_path, 'wb+') as destination:
                 for chunk in self.automotive_video.chunks():
                           destination.write(chunk)
            # Instantiate VideoFileClip object
            clip = VideoFileClip(temp_path)
            # Get video frame at 1 second
            temp_thumb = clip.get_frame(1)
            # Convert numpy array to pillow image and compress it
            self.vid_thumbnail = generate_video_thumbnail(temp_thumb)
        super(AutomotiveMedia, self).save(*args, **kwargs)


    class Meta:
        db_table = 'AutomotiveMedia'

# class AutomotiveView(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
#     automotive = models.ForeignKey(Automotive, on_delete=models.CASCADE, related_name="automotiveview_automotive")
#     viewer = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, related_name="automotiveview_viewer", null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

#     class Meta:
#         db_table = 'AutomotiveView'

#     def __str__(self):
#         return f"{self.automotive.name} viewed by {self.viewer.user.username}"

class ContactAutomotive(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True, related_name="contactautomotive_profile")
    automotive = models.ForeignKey(Automotive, on_delete=models.CASCADE, null=True, blank=True, related_name="contactautomotive_automotive")
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.automotive)

    class Meta:
        db_table = 'ContactAutomotive'


class ReportAutomotive(models.Model):
    REPORT_CHOICES = [
        ('Fraud', 'Fraud'),
        ('Offensive content', 'Offensive content'),
        ('Duplicate ad', 'Duplicate ad'),
        ('Product alread sold', 'Product alread sold'),
        ('Other', 'Other'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True, related_name="reportautomotive_profile")
    automotive = models.ForeignKey(Automotive, on_delete=models.CASCADE, null=True, blank=True, related_name="reportautomotive_automotive")
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    report_type = models.CharField(max_length=255, choices=REPORT_CHOICES, default='Other', null=True, blank=True)

    message = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.automotive)

    class Meta:
        db_table = 'ReportAutomotive'


class FavouriteAutomotive(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True, related_name="favouriteautomotive_profile")
    automotive = models.ForeignKey(Automotive, on_delete=models.CASCADE, null=True, blank=True, related_name="favouriteautomotive_automotive")
    is_deleted = models.BooleanField(default=False)
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.automotive)

    class Meta:
        db_table = 'FavouriteAutomotive'
        unique_together = ('profile', 'automotive')


class AutomotiveComparison(models.Model):
    automotive1 = models.ForeignKey(Automotive, on_delete=models.CASCADE, related_name="automotivecomparison_automotive1")
    automotive2 = models.ForeignKey(Automotive, on_delete=models.CASCADE, related_name="automotivecomparison_automotive2")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.automotive1.name} - {self.automotive2.name}"

    class Meta:
        db_table = "AutomotiveComparison"

class AutomotiveSearchHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True, related_name="automotivesearchhistory_profile")
    automotive = models.ForeignKey(Automotive, on_delete=models.CASCADE, null=True, blank=True, related_name="automotivesearchhistory_autotomotive")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'AutomotiveSearchHistory'

