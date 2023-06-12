
from ast import arg
from email.policy import default
from operator import mod
import uuid
from django.db import models
from . constants import s3_compress_image, generate_video_thumbnail
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
from classified_app.models import *
from community_app.models import *
import tempfile
import subprocess

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


YOUONLINE_PRIVACY_CHOICES = [
        ('Public', 'Public'),
        ('OnlyMe', 'OnlyMe'),
        ('Friends', 'Friends'),
    ]


# Location Module
class Country(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    counter = models.BigIntegerField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=256)
    country_code = models.CharField(max_length=32, null=True, blank=True)
    dial_code = models.CharField(max_length=16, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Country"


class State(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    counter = models.BigIntegerField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=256)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "State"


class City(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    counter = models.BigIntegerField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=256)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "City"


class Language(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    rtl = models.BooleanField(default=False)

    class Meta:
        db_table = 'Language'

    def __str__(self):
        return f"{self.name} - {self.code}"


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)

        profile = Profile.objects.create(
            user=user,
            gender='Male',
        )

        pp_album = ProfilePictureAlbum.objects.create(
            profile=profile
        )
        profile_picture = ProfilePicture.objects.create(
            album = pp_album
        )
        user_pp = UserProfilePicture.objects.create(
            profile = profile,
            picture = profile_picture
        )
        
        pc_album = ProfileCoverAlbum.objects.create(
            profile=profile
        )
        cover_picture = CoverPicture.objects.create(
            album = pc_album
        )
        user_cp = UserCoverPicture.objects.create(
            profile = profile,
            cover = cover_picture
        )
        privacy = UserPrivacySettings.objects.create(profile=profile)
        try:
            single_relationship = Relationship.objects.get(relationship_type="Single")
            relationship_status = RelationshipStatus.objects.create(
                    profile=profile,
                    relationship=single_relationship
                )
        except:
            relationship_status = RelationshipStatus.objects.create(profile = profile)

        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser):
    SOCIAL_PLATFORM_CHOICES = [
        ('Google', 'Google'),
        ('Facebook', 'Facebook'),
        ('Twitter', 'Twitter'),
        ('Apple', 'Apple'),
    ]
    # Required Fields

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # User Defined Fields

    first_name = models.CharField(max_length=128)
    middle_name = models.CharField(max_length=128, null=True, blank=True)
    last_name = models.CharField(max_length=128, null=True, blank=True)
    maiden_name = models.CharField(max_length=128, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    social_account = models.BooleanField(default=False)
    social_platform = models.CharField(max_length=32, choices=SOCIAL_PLATFORM_CHOICES, null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = MyAccountManager()

    def __str__(self):
        return self.username

    # For checking permissions. to keep it simple all admin have ALL permissons
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True


class Profile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ]
    PRIVACY_CHOICES = [
        ('Hide', 'Hide'),
        ('Show', 'Show')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="profile_user")
    gender = models.CharField(max_length=64, choices=GENDER_CHOICES, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    
    
    # Location
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="profile_country")
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name="profile_state")
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name="profile_city")

    street_adress = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)

    mobile_privacy = models.CharField(max_length=64, choices=PRIVACY_CHOICES, default='Show')
    special_offer_privacy = models.CharField(max_length=64, choices=PRIVACY_CHOICES, default='Show')
    recommended_privacy = models.CharField(max_length=64, choices=PRIVACY_CHOICES, default='Show')

    dial_code = models.CharField(max_length=200, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    current_city = models.CharField(max_length=200, blank=True, null=True)
    home_town = models.CharField(max_length=200, blank=True, null=True)
    religious_view = models.TextField(blank=True, null=True)
    political_view = models.TextField(blank=True, null=True)
    birth_place = models.CharField(max_length=200, blank=True, null=True)
    language = models.CharField(max_length=200, blank=True, null=True)
    alter_mobile = models.CharField(max_length=20, null=True, blank=True)
    facebook = models.CharField(max_length=200, blank=True, null=True)
    google = models.CharField(max_length=200, blank=True, null=True)
    twitter = models.CharField(max_length=200, blank=True, null=True)
    linkedin = models.CharField(max_length=200, blank=True, null=True)
    skype = models.CharField(max_length=200, blank=True, null=True)
    website = models.CharField(max_length=200, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    remove_at = models.DateTimeField(null=True, blank=True)
    is_blocked = models.BooleanField(default=False)
    is_reported = models.BooleanField(default=False)
    blog_author = models.BooleanField(default=False)

    class Meta:
        db_table = 'Profile'

    def __str__(self):
        return f"{self.id} - {self.user.username}"

class BlockProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile =  models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="blockprofile_profile")
    blocked_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="blockprofile_blocked_user")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        db_table = 'BlockProfile'

    def __str__(self):
        return f"{self.id}"

class ProfileStory(models.Model):
    STORY_CHOICES = [
        ("Text", "Text"),
        ("Media", "Media")
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="profile_profilestory")
    post = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True, related_name="post_profilestory")
    text = models.CharField(max_length=255, null=True, blank=True)
    font_family = models.CharField(max_length=128, null=True, blank=True)
    background_color = models.CharField(max_length=128, null=True, blank=True)
    text_color = models.CharField(max_length=128, null=True, blank=True)
    media_image = models.FileField(upload_to='UserStories/%Y/%m', null=True, blank=True)
    media_video = models.FileField(upload_to='UserStories/%Y/%m', null=True, blank=True)
    video_thumbnail = models.ImageField(upload_to='UserStories/%Y/%m', null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    x_axis = models.FloatField(default=0.00)
    y_axis = models.FloatField(default=0.00)
    angle = models.FloatField(default=0.00)
    story_type = models.CharField(max_length=32, choices=STORY_CHOICES, default="Text")
    privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default="Public")
    except_friends = models.ManyToManyField(Profile, blank=True, related_name='privacy_except_friends')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_compressed = models.BooleanField(default=False)
    video_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)

    class Meta:
        db_table = 'ProfileStory'

    def __str__(self):
        return self.profile.user.username


    def save(self, *args, **kwargs):
        if self.media_image and not self.is_compressed:
            self.media_image = s3_compress_image(self.media_image)
            self.is_compressed = True
        if self.media_video and not self.video_thumbnail:
            # Generate Video Thumnail
            # Get Temporary File Path
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_path = temp_file.name
            with open(temp_path, 'wb+') as destination:
                 for chunk in self.media_video.chunks():
                           destination.write(chunk)
            # Instantiate VideoFileClip object
            clip = VideoFileClip(temp_path)
            # Get video frame at 1 second
            temp_thumb = clip.get_frame(1)
            # Convert numpy array to pillow image and compress it
            self.video_thumbnail = generate_video_thumbnail(temp_thumb)
        super(ProfileStory, self).save(*args, **kwargs)
        

class StoryView(models.Model):
    story = models.ForeignKey(ProfileStory, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'StoryView'

    def __str__(self):
        return f"{self.story} viewed by {self.profile.user.username}"


class ProfileView(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="profileview_profile")
    viewer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="profileview_viewer")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'ProfileView'

    def __str__(self):
        return f"{self.profile.user.username} viewed by {self.viewer.user.username}"


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="post_profile")
    group = models.ForeignKey('community_app.Group', on_delete=models.CASCADE, null=True, blank=True, related_name="post_group")
    page = models.ForeignKey('community_app.Page', on_delete=models.CASCADE, null=True, blank=True, related_name="post_page")
    feeling = models.CharField(max_length=128, null=True, blank=True)
    feeling_unicode = models.CharField(max_length=128, null=True, blank=True)
    activity = models.CharField(max_length=128, null=True, blank=True)
    activity_unicode = models.CharField(max_length=128, null=True, blank=True)
    privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default='Public')
    is_deleted = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    is_declined = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    # Location
    street_adress = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)

    text = models.TextField(null=True, blank=True)
    reactions_count = models.BigIntegerField(default=0, null=True, blank=True)
    dislikes_count = models.BigIntegerField(default=0, null=True, blank=True)
    comments_count = models.BigIntegerField(default=0, null=True, blank=True)
    # When Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    # PostTypes
    poll_post = models.BooleanField(default=False)
    video_module = models.BooleanField(default=False)
    media_post = models.BooleanField(default=False)
    video_post = models.BooleanField(default=False)
    profile_picture_post = models.BooleanField(default=False)
    cover_post = models.BooleanField(default=False)
    normal_post = models.BooleanField(default=False)
    shared_post = models.BooleanField(default=False)
    album_post = models.BooleanField(default=False)
    property_post = models.BooleanField(default=False)
    automotive_post = models.BooleanField(default=False)
    classified_post = models.BooleanField(default=False)
    business_directory_post=models.BooleanField(default=False)
    group_post = models.BooleanField(default=False)
    group_banner = models.BooleanField(default=False)
    group_logo = models.BooleanField(default=False)
    page_post = models.BooleanField(default=False)
    page_banner = models.BooleanField(default=False)
    page_logo = models.BooleanField(default=False)
    story_post = models.BooleanField(default=False)
    blog_post = models.BooleanField(default=False)
    job_post = models.BooleanField(default=False)
    job_project_post = models.BooleanField(default=False) 
    birthday_post = models.BooleanField(default=False)
    is_reported = models.BooleanField(default=False)
    product_post = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    class Meta:
        # ordering = ('-created_at',)
        db_table = 'Post'


class Relationship(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    relationship_type = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        db_table = 'Relationship'

    def __str__(self):
        return self.relationship_type


class RelationshipStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    relationship = models.ForeignKey(Relationship, on_delete=models.CASCADE, null=True, blank=True)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name='profile_relationship')
    partner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name='partner_relationship')
    privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default='OnlyMe', null=True, blank=True)
    since = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'RelationshipStatus'

    def __str__(self):
        return self.profile.user.username


class UserAlbum(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="useralbum_profile")
    album_title = models.CharField(max_length=500, blank=False, null=False)
    description = models.TextField(null=True, blank=True)
    privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default='Public')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'UserAlbum'


class UserAlbumMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    album = models.ForeignKey(UserAlbum, on_delete=models.CASCADE, related_name="useralbummedia_album")
    image = models.ImageField(upload_to='AlbumImages/%Y/%m', null=True, blank=True)
    video = models.FileField(upload_to='AlbumVideos/%Y/%m', null=True, blank=True)
    vid_thumbnail = models.FileField(upload_to='AlbumVideos/%Y/%m', null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name="useralbummedia_post")
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_compressed = models.BooleanField(default=False)
    video_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)

    class Meta:
        db_table = 'UserAlbumMedia'


    def save(self, *args, **kwargs):
        if self.image and not self.is_compressed:
            self.image = s3_compress_image(self.image)
            self.is_compressed = True
        if self.video and not self.vid_thumbnail:
            # Generate Video Thumnail
            # Get Temporary File Path
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_path = temp_file.name
            with open(temp_path, 'wb+') as destination:
                 for chunk in self.video.chunks():
                           destination.write(chunk)
            # Instantiate VideoFileClip object
            clip = VideoFileClip(temp_path)
            # Get video frame at 1 second
            temp_thumb = clip.get_frame(1)
            # Convert numpy array to pillow image and compress it
            self.vid_thumbnail = generate_video_thumbnail(temp_thumb)
        super(UserAlbumMedia, self).save(*args, **kwargs)


# This table is used for creating a post when we create an album
# or add something to an existing album
class AlbumPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    media_posts = models.ManyToManyField(Post, blank=True, related_name="albumpost_mediaposts")
    album = models.ForeignKey(UserAlbum, on_delete=models.CASCADE, related_name="albumpost_album")
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE, related_name="albumpost_post")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'AlbumPost'

    def __str__(self):
        try:
            return f"{self.id} - {self.post.id}"
        except:
            return str(self.id)


class UserFamilyRelation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    relationship_name = models.CharField(max_length=256, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'UserFamilyRelation'

    def __str__(self):
        return self.relationship_name


class UserFamilyMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name='family_profile')
    relation = models.ForeignKey(UserFamilyRelation, on_delete=models.CASCADE, null=True, blank=True)
    family_member = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True, related_name='family_member_profile')
    privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default='Friends', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        db_table = 'UserFamilyMember'


class UserLifeEventCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    category_name = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'UserLifeEventCategory'

    def __str__(self):
        return self.category_name


class UserLifeEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    category = models.ForeignKey(UserLifeEventCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=500, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'UserLifeEvent'

    def __str__(self):
        return self.profile.user.username


class ProfileCoverAlbum(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='cover_album_profile')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'ProfileCoverAlbum'


class CoverPicture(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='cover_picture')
    album = models.ForeignKey(ProfileCoverAlbum, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='cover_album')
    cover = models.ImageField(max_length=255, null=True, blank=True, upload_to='covers')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name="post_cover")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.cover and not self.is_compressed:
            self.cover = s3_compress_image(self.cover)
            self.is_compressed = True
        super(CoverPicture, self).save(*args, **kwargs)


    class Meta:
        db_table = 'CoverPicture'


class UserCoverPicture(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='cover_profile')
    cover = models.OneToOneField(CoverPicture, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='cover_cover')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'UserCoverPicture'


class ProfilePictureAlbum(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='picture_album_profile')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'ProfilePictureAlbum'

    def __str__(self):
        return self.profile.user.username


class ProfilePicture(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='profile_picture')
    album = models.ForeignKey(ProfilePictureAlbum, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='picture_album')
    picture = models.ImageField(max_length=255, null=True, blank=True, upload_to='pictures')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name="post_profile_picture")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.picture and not self.is_compressed:
            self.picture = s3_compress_image(self.picture)
            self.is_compressed = True
        super(ProfilePicture, self).save(*args, **kwargs)


    class Meta:
        db_table = 'ProfilePicture'


class UserProfilePicture(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='picture_profile')
    picture = models.OneToOneField(ProfilePicture, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='picture_picture')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'UserProfilePicture'

    def __str__(self):
        return self.profile.user.username


class UserWorkPlace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=256, null=True, blank=True)
    employment_type = models.CharField(max_length=256, null=True, blank=True)
    company = models.CharField(max_length=256, null=True, blank=True)
    
    # Location
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="userworkplace_country")
    street_adress = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)

    currently_working = models.BooleanField(default=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default='Public')
    description = models.CharField(max_length=512, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'UserWorkPlace'

    def __str__(self):
        return self.title


class UserPlacesLived(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="userplaceslived_profile")
    address = models.CharField(max_length=500, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="userplaceslived_country")
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name="userplaceslived_state")
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name="userplaceslived_city")
    zip_code = models.CharField(max_length=64, null=True, blank=True)
    moved_in = models.DateField(null=True, blank=True)
    moved_out = models.DateField(null=True, blank=True)
    currently_living = models.BooleanField(default=True)
    privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default='Public')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'UserPlacesLived'


class UserAboutYou(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    about_you = models.TextField(max_length=500, null=True, blank=True)
    favourite_quote = models.TextField(max_length=500, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'UserAboutYou'


class UserUniversity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    university_name = models.CharField(max_length=500, null=True, blank=True)
    degree = models.CharField(max_length=500, null=True, blank=True)
    major = models.CharField(max_length=128, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    currently_Studying = models.BooleanField(default=False)
    privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default='Public')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'UserUniversity'


class LoginHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    ip = models.CharField(max_length=500, null=True, blank=True)
    login_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'LoginHistory'


class UserHighSchool(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # ForeignKeys
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="userhighschool_profile")
    country = models.ForeignKey('youonline_social_app.Country', on_delete=models.CASCADE, null=True, blank=True)
    city = models.ForeignKey('youonline_social_app.City', on_delete=models.CASCADE, null=True, blank=True)

    school_name = models.CharField(max_length=500, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    graduation_year = models.DateField(null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    currently_Studying = models.BooleanField(default=False)
    privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default='Public')

    degree = models.CharField(max_length=500, null=True, blank=True)
    major_subject = models.CharField(max_length=500, null=True, blank=True)
    degree_type = models.CharField(max_length=500, null=True, blank=True)
    group = models.CharField(max_length=500, null=True, blank=True)
    specialization = models.CharField(max_length=500, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'UserHighSchool'


class VerificationCode(models.Model):
    # Foreign Key
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    code = models.CharField(max_length=20, null=True, blank=True)
    used = models.BooleanField(default=False)
    expired = models.BooleanField(default=False)

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.code)

    def get_username(self):
        return str(self.user.username) if self.user else 'N/A'

    class Meta:
        db_table = 'VerificationCode'


class UserPrivacySettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True, blank=True)
    follow_privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default='Public')
    friend_request_privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default='Public')
    see_friends_privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default='Public')
    contact_info_privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default='Public')
    search_profile_privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default='Public')
    see_birthday_privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default='Public')
    timeline_post_privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default='Public')
    activities_privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default='Public')
    status_privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default='Public')
    street_adress_privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default='Public')
    see_followers_privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default='Public')

    def __str__(self):
        return self.profile.user.username


# Post Module
class Poll(models.Model):
    POLL_DURATION_CHOICES = [
        ('24Hours', '24Hours'),
        ('3Days', '3Days'),
        ('1Week', '1Week'),
        ('2Weeks', '2Weeks'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    description = models.TextField(null=True, blank=True)
    duration = models.CharField(max_length=32, choices=POLL_DURATION_CHOICES, default='24Hours')
    total_votes = models.BigIntegerField(default=0)
    
    # Foreign Keys
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="poll_profile")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name="pollpost_post")

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    expire_at = models.DateTimeField(null=True, blank=True)
    is_expired = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.description)

    class Meta:
        db_table = 'Poll'

class YouonlineLogo(models.Model):
    logo = models.ImageField(upload_to='logo/', max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class PollOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, null=True, blank=True, related_name="polloption_poll")
    option = models.TextField(null=True, blank=True)
    total_votes = models.BigIntegerField(default=0)

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.option} - {self.poll.description}"

    class Meta:
        db_table = 'PollOption'


class PollVote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, null=True, blank=True, related_name="pollvote_poll")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="pollvote_profile")
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, null=True, blank=True, related_name="pollvote_option")

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.option)

    class Meta:
        db_table = 'PollVote'


class PostMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='post_post')
    sub_post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='sub_post')

    post_image = models.ImageField(upload_to='post_images/%Y/%m', max_length=255, null=True, blank=True)
    post_video = models.FileField(upload_to='post_videos/%Y/%m', max_length=255, null=True, blank=True)
    vid_thumbnail = models.ImageField(upload_to='post_videos/%Y/%m', max_length=255, null=True, blank=True)
    post_audio = models.FileField(upload_to='post_audios/%Y/%m', max_length=255, null=True, blank=True)
    post_gif = models.CharField(max_length=255, null=True, blank=True)
    background_image = models.FileField(upload_to='background_images/%Y/%m', max_length=255, null=True, blank=True)
    background_color = models.TextField(null=True, blank=True)
    reactions_count = models.BigIntegerField(default=0, null=True, blank=True)
    comments_count = models.BigIntegerField(default=0, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_compressed = models.BooleanField(default=False)
    video_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)

    def __str__(self):
        return str(self.post)

    def save(self, *args, **kwargs):
        # Compress Image
        if self.post_image and not self.is_compressed:
            self.post_image = s3_compress_image(self.post_image)
            self.is_compressed = True
        if self.background_image and not self.is_compressed:
            self.background_image = s3_compress_image(self.background_image)
            self.is_compressed = True
        if self.post_video and not self.vid_thumbnail:
            # Generate Video Thumnail
            # Get Temporary File Path
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_path = temp_file.name
            with open(temp_path, 'wb+') as destination:
                 for chunk in self.post_video.chunks():
                           destination.write(chunk)
            # Instantiate VideoFileClip object
            clip = VideoFileClip(temp_path)
            # Get video frame at 1 second
            temp_thumb = clip.get_frame(1)
            # Convert numpy array to pillow image and compress it
            self.vid_thumbnail = generate_video_thumbnail(temp_thumb)
        super(PostMedia, self).save(*args, **kwargs)
        
    class Meta:
        db_table = 'PostMedia'


class MediaPostObject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    parent_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="parent_post")
    child_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="child_post")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.parent_post.text

    class Meta:
        db_table = 'MediaPostObject'


class SharedPost(models.Model):
    SHARE_CHOICES = [
        ('NewsFeed', 'NewsFeed'),
        ('FriendTimeline', 'FriendTimeline'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name='sharedpost_profile')
    # This is the post that is being shared.
    shared_post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='sharedpost_sharedpost')
    # This is the new post created after user shares a post
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='sharedpost_post')
    share_choice = models.CharField(max_length=32, choices=SHARE_CHOICES, default='NewsFeed')
    friend = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name='sharedpost_friend')
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.post)

    class Meta:
        db_table = 'SharedPost'


class PostReaction(models.Model):
    REACTION_CHOICES =  [
        ('like', 'like'),
        ('love', 'love'),
        ('haha', 'haha'),
        ('wow', 'wow'),
        ('sad', 'sad'),
        ('angry', 'angry'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name="postreaction_post")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="postreaction_profile")
    type = models.CharField(max_length=32, choices=REACTION_CHOICES, null=True, blank=True)
    react_unicode = models.CharField(max_length=128, null=True, blank=True)

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.post)

    class Meta:
        db_table = 'PostReaction'


class PostDislike(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name="postdislike_post")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="postdislike_profile")
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.post)

    class Meta:
        db_table = 'PostDislike'
        unique_together = ("post", "profile")


class PostComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    reactions_count = models.BigIntegerField(default=0, null=True, blank=True)
    replies_count = models.BigIntegerField(default=0, null=True, blank=True)

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.post)

    class Meta:
        db_table = 'PostComment'


class SavedPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='savedpost_profile')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='savedpost_post')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.profile.user.username

    class Meta:
        db_table = 'SavedPost'
        unique_together = ('profile', 'post')


class HiddenPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='hidden_profile')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='hidden_post')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.profile.user.username

    class Meta:
        db_table = 'HiddenPost'
        unique_together = ('profile', 'post')


class CommentMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, null=True, blank=True)

    comment_image = models.ImageField(upload_to='comment_images/%Y/%m', null=True, blank=True)
    comment_video = models.FileField(upload_to='comment_videos/%Y/%m', null=True, blank=True)
    comment_audio = models.FileField(upload_to='comment_audios/%Y/%m', null=True, blank=True)
    comment_gif = models.CharField(max_length=255, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_compressed = models.BooleanField(default=False)
    video_compressed = models.BooleanField(default=False)
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    bucket_uploaded = models.BooleanField(default=False)

    def __str__(self):
        return str(self.comment)

    def save(self, *args, **kwargs):
        if self.comment_image and not self.is_compressed:
            self.comment_image = s3_compress_image(self.comment_image)
            self.is_compressed = True
        super(CommentMedia, self).save(*args, **kwargs)
        

    class Meta:
        db_table = 'CommentMedia'


class CommentReaction(models.Model):
    REACTION_CHOICES =  [
        ('like', 'like'),
        ('love', 'love'),
        ('haha', 'haha'),
        ('wow', 'wow'),
        ('sad', 'sad'),
        ('angry', 'angry'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=32, choices=REACTION_CHOICES, null=True, blank=True)
    react_unicode = models.CharField(max_length=128, null=True, blank=True)

    # WHO Columns
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.comment)

    class Meta:
        db_table = 'CommentReaction'


class CommentReply(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    reactions_count = models.BigIntegerField(default=0, null=True, blank=True)

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.comment)

    class Meta:
        db_table = 'CommentReply'


class CommentReplyMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    comment_reply = models.ForeignKey(CommentReply, on_delete=models.CASCADE, null=True, blank=True)

    reply_image = models.ImageField(upload_to='reply_images/%Y/%m', null=True, blank=True)
    reply_video = models.FileField(upload_to='reply_videos/%Y/%m', null=True, blank=True)
    reply_audio = models.FileField(upload_to='reply_audios/%Y/%m', null=True, blank=True)
    reply_gif = models.CharField(max_length=255, null=True, blank=True)
    reactions_count = models.BigIntegerField(default=0, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_compressed = models.BooleanField(default=False)
    video_compressed = models.BooleanField(default=False)
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    bucket_uploaded = models.BooleanField(default=False)

    def __str__(self):
        return str(self.comment_reply)

    def save(self, *args, **kwargs):
        if self.reply_image:
            self.reply_image = s3_compress_image(self.reply_image)
            self.is_compressed = True
        super(CommentReplyMedia, self).save(*args, **kwargs)
        
    
    class Meta:
        db_table = 'CommentReplyMedia'


class CommentReplyReaction(models.Model):
    REACTION_CHOICES =  [
        ('like', 'like'),
        ('love', 'love'),
        ('haha', 'haha'),
        ('wow', 'wow'),
        ('sad', 'sad'),
        ('angry', 'angry'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    comment = models.ForeignKey(CommentReply, on_delete=models.CASCADE, null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=32, choices=REACTION_CHOICES, null=True, blank=True)
    react_unicode = models.CharField(max_length=128, null=True, blank=True)

    # WHO Columns
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.comment)

    class Meta:
        db_table = 'CommentReplyReaction'


class TagUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    tagged_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="taguser_taggedprofile")
    tagged_by = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="taguser_taggedby")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name="taguser_post")
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, null=True, blank=True, related_name="taguser_comment")
    reply_comment = models.ForeignKey(CommentReply , on_delete=models.CASCADE , null=True, blank=True, related_name='taguser_comment_reply')
    is_mentioned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.tagged_profile.user.username

    def is_comment(self):
        if self.comment:
            return True
        return False

    def is_post(self):
        if self.post:
            return True
        return False

    def is_comment_reply(self):
        if self.reply_comment:
            return True
        return False

    class Meta:
        db_table = 'TagUser'


# Friends Module
class FriendsList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='friends_profile')
    friends = models.ManyToManyField(Profile, blank=True, related_name='friends_list')
    followers = models.ManyToManyField(Profile, blank=True, related_name='followers_list')
    following = models.ManyToManyField(Profile, blank=True, related_name='following_list')

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.profile.user.username


class FriendRequest(models.Model):
    REQUEST_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    req_sender = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name='req_sender')
    req_receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='req_receiver')
    status = models.CharField(max_length=16, choices=REQUEST_CHOICES, default='Pending')
    is_active = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)


class IgnoredList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name='ignoredpeople_profile')
    people = models.ManyToManyField(Profile, blank=True)
    groups = models.ManyToManyField('community_app.Group', blank=True)
    pages = models.ManyToManyField('community_app.Page', blank=True)
    classifieds = models.ManyToManyField('classified_app.Classified', blank=True)
    properties = models.ManyToManyField('property_app.Property', blank=True)
    automotives = models.ManyToManyField('automotive_app.Automotive', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return str(self.profile.user.username)

    class Meta:
        db_table = 'IgnoredList'


# Notifications Module
# This table is specifically placed for notifiers listing where a user decides to get notification for a post/comment/comment_reply.
class NotifiersList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    notifiers_list = models.ManyToManyField(Profile, related_name='notifierslist_profile', blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name="notifierslist_post")
    post_comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, null=True, blank=True, related_name="notifierslist_postcomment")
    comment_reply = models.ForeignKey(CommentReply, on_delete=models.CASCADE, null=True, blank=True, related_name="notifierslist_commentreply")

    class Meta:
        db_table = 'NotifiersList'


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    type = models.CharField(max_length=64, null=True, blank=True)
    text = models.CharField(max_length=128, null=True, blank=True)
    notifiers_list = models.ManyToManyField(Profile, related_name='notifiers_list', blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name="notification_post")
    
    automotive = models.ForeignKey(Automotive, on_delete=models.CASCADE, null=True, blank=True, related_name="notification_automotive")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True, related_name="notification_job")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True, related_name="notification_property")
    classified = models.ForeignKey(Classified, on_delete=models.CASCADE, null=True, blank=True, related_name="notification_classified")

    story = models.ForeignKey('ProfileStory', on_delete=models.CASCADE, null=True, blank=True, related_name="notification_profilestory")
    post_comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, null=True, blank=True, related_name="notification_post_comment")
    comment_reply = models.ForeignKey(CommentReply, on_delete=models.CASCADE, null=True, blank=True, related_name="notification_comment_reply")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="notification_profile")
    group = models.ForeignKey('community_app.Group', on_delete=models.CASCADE, null=True, blank=True, related_name="notification_group")
    page = models.ForeignKey('community_app.Page', on_delete=models.CASCADE, null=True, blank=True, related_name="notification_page")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    read_by = models.ManyToManyField(Profile, related_name='read_notif_profile', blank=True)

    def __str__(self):
        return str(self.type)

    def notifiers_count(self):
        return str(len(self.notifiers_list.all()))


    class Meta:
        db_table = 'Notification'

class ExceptionRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    content = models.JSONField(default='')

    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f'{self.id}'


class UserActivity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="useractivity_profile")
    activity = models.TextField(null=True, blank=True)
    interest = models.TextField(null=True, blank=True)
    favorite_music = models.TextField(null=True, blank=True)
    favorite_movie = models.TextField(null=True, blank=True)
    favorite_tv_show = models.TextField(null=True, blank=True)
    favorite_book = models.TextField(null=True, blank=True)
    favorite_game = models.TextField(null=True, blank=True)
    favorite_quote = models.TextField(null=True, blank=True)
    about_me = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        db_table = 'UserActivity'

class ReportProfileCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f'{self.title}'
    
    class Meta:
        db_table = 'ReportProfileCategory'
    

class ReportProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    reported_by = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="reportprofile_profile")
    reported_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="reportprofile_reported_profile")
    category = models.ForeignKey(ReportProfileCategory, on_delete=models.CASCADE, null=True, blank=True, related_name="reportprofile_category")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        db_table = 'ReportProfile'


class ReportPostCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f'{self.title}'
    
    class Meta:
        db_table = 'ReportPostCategory'

class ReportPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name="reportpost_post")
    reported_by = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="reportpost_profile")
    category = models.ForeignKey(ReportPostCategory, on_delete=models.CASCADE, null=True, blank=True, related_name="reportpost_category")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        db_table = 'ReportPost'


class CompanyMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True)

    automotive = models.OneToOneField(Automotive, on_delete=models.CASCADE, null=True, blank=True)
    property = models.OneToOneField(Property, on_delete=models.CASCADE, null=True, blank=True)
    job = models.OneToOneField(Job, on_delete=models.CASCADE, null=True, blank=True)

    # Media
    logo = models.ImageField(max_length=256, upload_to='Company/Logo/%Y/%m', null=True)
    is_deleted = models.BooleanField(default=False)
    is_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)
    
    is_automotive = models.BooleanField(default=False)
    is_property = models.BooleanField(default=False)
    is_job = models.BooleanField(default=False)

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'CompanyMedia'
    
    def save(self, *args, **kwargs):
        # Compress Image
        if self.logo and not self.is_compressed:
            self.logo = s3_compress_image(self.logo)
            self.is_compressed = True
        super(CompanyMedia, self).save(*args, **kwargs)


class PackagePlan(models.Model):
    PLANE_CHOICES = [
        ('Basic', 'Basic Plan'),
        ('Standard', 'Standard Plan'),
        ('Premium', 'Premium Plan'),
    ]
    DURATION_CHOICES = [
        ('1 Week', '1 Week'),
        ('2 Week', '2 Week'),
        ('3 Week', '3 Week'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=512, choices=PLANE_CHOICES, null=True, blank=True)
    subject = models.TextField(null=True, blank=True, default='Make your ad featured')
    description = models.TextField(null=True, blank=True, default='Customer support')
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.ForeignKey('job_app.Currency', on_delete=models.CASCADE, null=True, blank=True)
    featured_week = models.CharField(max_length=512, choices=DURATION_CHOICES, null=True, blank=True)

    # WHO
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'PackagePlan'

class PackagePlaneDetail(models.Model):
    TYPE_CHOICES = [
        ('Classified', 'Classified'),
        ('Automotive', 'Automotive'),
        ('Property', 'Property'),
        ('Job', 'Job'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    plan = models.ForeignKey(PackagePlan, on_delete=models.CASCADE, null=True, blank=True)

    automotive = models.ForeignKey(Automotive, on_delete=models.CASCADE, null=True, blank=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True)
    classified = models.ForeignKey(Classified, on_delete=models.CASCADE, null=True, blank=True)
    packege_type = models.CharField(max_length=512, choices=TYPE_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'PackagePlaneDetail'

class ModuleViewHistory(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True)
    automotive = models.ForeignKey(Automotive, on_delete=models.CASCADE, null=True, blank=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True)
    classified = models.ForeignKey(Classified, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'ModuleViewHistory'

class DealData(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    automotive = models.ForeignKey(Automotive, on_delete=models.CASCADE, null=True, blank=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)
    classified = models.ForeignKey(Classified, on_delete=models.CASCADE, null=True, blank=True)

    discount_percentage = models.IntegerField(null=True, blank=True)
    discounted_price = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    deal_automotive = models.BooleanField(default=False)
    deal_property = models.BooleanField(default=False)
    deal_classified = models.BooleanField(default=False)
    
    is_expired = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'DealData'


