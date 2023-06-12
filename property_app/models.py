import uuid
from django.db import models
from youonline_social_app.constants import s3_compress_image, create_slug
from youonline_social_app.models import *
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from PIL import Image
from django.core.files.storage import default_storage as storage
import random, string
from moviepy.editor import VideoFileClip
from django.conf import settings
import time
import tempfile


YOUONLINE_PRIVACY_CHOICES = [
        ('Public', 'Public'),
        ('OnlyMe', 'OnlyMe'),
        ('Friends', 'Friends'),
    ]

# Property Models
class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255)
    image = models.FileField(null=True, blank=True, upload_to='category/images')

    view_count = models.BigIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'PropertyCategory'

    def __str__(self):
        return str(self.title)


class SubCategory(models.Model):
    category = models.ForeignKey(Category, related_name='sub_category', on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    image = models.FileField(null=True, blank=True, upload_to='subcategory/images')

    title = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'PropertySubCategory'

    def __str__(self):
        return str(self.title)


class SubSubCategory(models.Model):
    sub_category = models.ForeignKey(SubCategory, related_name='sub_sub_category', on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    image = models.FileField(null=True, blank=True, upload_to='subsubcategory/images')

    title = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'PropertySubSubCategory'

    def __str__(self):
        return str(self.title)


class PropertyFeatures(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'PropertyFeatures'

    def __str__(self):
        return str(self.name)


class Property(models.Model):
    BEDROOM_CHOICES = [
        ('01', '01'),
        ('02', '02'),
        ('03', '03'),
        ('04', '04'),
        ('05', '05'),
        ('06+', '06+'),
        ('Studio', 'Studio'),
    ]
    BATH_CHOICES = [
        ('01', '01'),
        ('02', '02'),
        ('03', '03'),
        ('04', '04'),
        ('05', '05'),
        ('06', '06'),
        ('07+', '07+'),
    ]
    LIVING_ROOM_CHOICES = [
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4+', '4+'),
    ]
    BALCONY_CHOICES = [
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4+', '4+'),
    ]
    LIFT_CHOICES = [
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4+', '4+'),
    ]
    PARKING_CHOICES = [
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4+', '4+'),
    ]
    STORAGE_CHOICES = [
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4+', '4+'),
    ]
    GYM_CHOICES = [
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4+', '4+'),
    ]
    CINEMA_CHOICES = [
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4+', '4+'),
    ]
    CONFERENCE_CHOICES = [
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4+', '4+'),
    ]
    SWIMMING_POLL_CHOICES = [
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4+', '4+'),
    ]
    MAID_ROOM_CHOICES = [
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4+', '4+'),
    ]
    SPORTS_CHOICES = [
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4+', '4+'),
    ]
    DURATION_CHOICES = [
        ('7 days', '7 days'),
        ('14 days', '14 days'),
        ('30 days', '30 days'),
    ]
    FURNISHED_CHOICES =[
        ('Furnished', 'Furnished'),
        ('Unfurnished', 'Unfurnished'),
    ]
    UNIT_CHOICES =[
        ('Kanal', 'Kanal'),
        ('Marla', 'Marla'),
        ('SquareFeet', 'Square Feet'),
        ('SquareMeter', 'Square Meter'),
        ('SquareYard', 'Square Yard'),
    ]

    VERIFICATION_STATUS = [
        ('Pending', 'Pending'),
        ('Verified', 'Verified'),
        ('Rejected', 'Rejected'),
    ]
    TYPE_CHOICES = [
        ('Rent', 'Rent'),
        ('Sale', 'Sale'),
    ]
    
    BUSINESS_CHOICES = [
        ('Individual', 'Individual'),
        ('Company', 'Company'),
    ]

    # Foreign Keys
    feature = models.ManyToManyField(PropertyFeatures, blank=True)
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey('youonline_social_app.Post', on_delete=models.CASCADE, null=True, blank=True, related_name='post_property')
    company = models.ForeignKey('job_app.Company', on_delete=models.CASCADE, null=True, blank=True, related_name='property_company')

    company_name = models.CharField(max_length=512, null=True, blank=True)
    company_license = models.CharField(max_length=512, null=True, blank=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True)
    sub_sub_category = models.ForeignKey(SubSubCategory, on_delete=models.CASCADE, null=True, blank=True)

    country = models.ForeignKey('youonline_social_app.Country', on_delete=models.CASCADE, null=True, blank=True)
    state = models.ForeignKey('youonline_social_app.State', on_delete=models.CASCADE, null=True, blank=True)
    city = models.ForeignKey('youonline_social_app.City', on_delete=models.CASCADE, null=True, blank=True)
    
    # Location
    street_adress = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    # Property Details
    area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    area_unit = models.CharField(max_length=255, choices=UNIT_CHOICES, null=True, blank=True)

    bedrooms = models.CharField(max_length=255, choices=BEDROOM_CHOICES, null=True, blank=True)
    baths = models.CharField(max_length=255, choices=BATH_CHOICES, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    # Pricing
    currency = models.ForeignKey('job_app.Currency', on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Contact Details
    mobile = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    # Amenities
    living_room = models.CharField(max_length=255, choices=LIVING_ROOM_CHOICES, null=True, blank=True)
    balcony = models.CharField(max_length=255, choices=BALCONY_CHOICES, null=True, blank=True)
    lift = models.CharField(max_length=255, choices=LIFT_CHOICES, null=True, blank=True)
    parking = models.CharField(max_length=255, choices=PARKING_CHOICES, null=True, blank=True)
    storage = models.CharField(max_length=255, choices=STORAGE_CHOICES, null=True, blank=True)
    gym = models.CharField(max_length=255, choices=GYM_CHOICES, null=True, blank=True)
    cinema = models.CharField(max_length=255, choices=CINEMA_CHOICES, null=True, blank=True)
    conference = models.CharField(max_length=255, choices=CONFERENCE_CHOICES, null=True, blank=True)
    swimming_poll = models.CharField(max_length=255, choices=SWIMMING_POLL_CHOICES, null=True, blank=True)
    maid_room = models.CharField(max_length=255, choices=MAID_ROOM_CHOICES, null=True, blank=True)
    sports = models.CharField(max_length=255, choices=SPORTS_CHOICES, null=True, blank=True)
    furnished = models.CharField(max_length=255, choices=FURNISHED_CHOICES, null=True, blank=True)
    property_type = models.CharField(max_length=255, choices=TYPE_CHOICES, null=True, blank=True)
    dial_code = models.CharField(max_length=255, null=True, blank=True)

    privacy = models.CharField(max_length=255, choices=YOUONLINE_PRIVACY_CHOICES, null=True, blank=True)
    business_type = models.CharField(max_length=255, choices=BUSINESS_CHOICES, null=True, blank=True)

    duration = models.CharField(max_length=255, choices=DURATION_CHOICES, null=True, blank=True)
    language = models.ForeignKey('youonline_social_app.Language', on_delete=models.CASCADE, null=True, blank=True)
    verification_status = models.CharField(max_length=255, choices=VERIFICATION_STATUS, default='Pending', null=True, blank=True)
    view_count = models.BigIntegerField(default=0)

    long = models.DecimalField(max_digits=30, decimal_places=16, null=True, blank=True)
    lat = models.DecimalField(max_digits=30, decimal_places=16,  null=True, blank=True)

    is_deal = models.BooleanField(default=False)
    is_active =  models.BooleanField(default=True)
    is_promoted = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            slugs = list(Property.objects.all().values_list('slug', flat=True))
            self.slug = create_slug(name=self.name, slugs=slugs)
        super(Property, self).save(*args, **kwargs)

    class Meta:
        db_table = 'Property'

    def __str__(self):
        return str(self.name)


class PropertyMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey('youonline_social_app.Post', on_delete=models.CASCADE, null=True, blank=True, related_name='propertymedia_post')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)
    # Media
    property_image = models.ImageField(max_length=256, upload_to='property_images/%Y/%m', null=True, blank=True)
    property_video = models.FileField(max_length=256, upload_to='property_videos/%Y/%m', null=True, blank=True)
    property_video_thumbnail = models.FileField(max_length=256, upload_to='property_videos_thumbnail/%Y/%m', null=True, blank=True)
    floor_image = models.ImageField(max_length=256, upload_to='property_floor_images/%Y/%m', null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_compressed = models.BooleanField(default=False)
    video_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.property)

    def save(self, *args, **kwargs):
        if self.property_image and not self.is_compressed:
            self.property_image = s3_compress_image(self.property_image)
            self.is_compressed = True
        if self.floor_image and not self.is_compressed:
            self.floor_image = s3_compress_image(self.floor_image)
            self.is_compressed = True
        # Generate Video Thumnail
        if self.property_video and not self.property_video_thumbnail:
            # Get Temporary File Path
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_path = temp_file.name
            with open(temp_path, 'wb+') as destination:
                 for chunk in self.property_video.chunks():
                           destination.write(chunk)
            # Instantiate VideoFileClip object
            clip = VideoFileClip(temp_path)
            # Get video frame at 1 second
            temp_thumb = clip.get_frame(1)
            # Convert numpy array to pillow image and compress it
            self.property_video_thumbnail = generate_video_thumbnail(temp_thumb)
        super(PropertyMedia, self).save(*args, **kwargs)
    
    class Meta:
        db_table = 'PropertyMedia'

# class PropertyView(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
#     property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="propertyview_property")
#     viewer = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, related_name="propertyview_viewer", null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

#     class Meta:
#         db_table = 'PropertyView'

#     def __str__(self):
#         return f"{self.property.name} viewed by {self.viewer.user.username}"

class ContactProperty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.property)

    class Meta:
        db_table = 'ContactProperty'


class ReportProperty(models.Model):
    REPORT_CHOICES = [
        ('Fraud', 'Fraud'),
        ('Offensive content', 'Offensive content'),
        ('Duplicate ad', 'Duplicate ad'),
        ('Product alread sold', 'Product alread sold'),
        ('Other', 'Other'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    report_type = models.CharField(max_length=255, choices=REPORT_CHOICES, default='Other', null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.property)

    class Meta:
        db_table = 'ReportProperty'


class FavouriteProperty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True, related_name="favouriteproperty_profile")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True, related_name="favouriteproperty_property")
    is_deleted = models.BooleanField(default=False)
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.property)

    class Meta:
        db_table = 'FavouriteProperty'
        unique_together = ('profile', 'property')


class PropertySearchHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True, related_name="propertysearchhistory_profile")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True, related_name="propertysearchhistory_property")
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.property.id)
    class Meta:
        db_table = 'PropertySearchHistory'


