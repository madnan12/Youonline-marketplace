from pyexpat import model
import uuid
from django.db import models
from youonline_social_app.constants import create_slug, generate_page_username, s3_compress_image
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
from youonline_social_app.models import *

YOUONLINE_PRIVACY_CHOICES = [
        ('Public', 'Public'),
        ('OnlyMe', 'OnlyMe'),
        ('Friends', 'Friends'),
    ]

# Group Models
class GroupCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=64)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "GroupCategory"


class Group(models.Model):
    WHO_CAN_POST_CHOICES = [
        ('adminonly', 'adminonly'),
        ('members', 'members'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=32, null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    category = models.ForeignKey(GroupCategory, on_delete=models.CASCADE, null=True, blank=True)
    privacy = models.CharField(max_length=255, choices=YOUONLINE_PRIVACY_CHOICES, default='Public')
    description = models.TextField(null=True, blank=True)
    who_can_post = models.CharField(max_length=16, choices=WHO_CAN_POST_CHOICES, default='members', null=True, blank=True)
    approval_required = models.BooleanField(default=False, null=True, blank=True)

    # Location
    street_adress = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    is_promoted=models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            slugs = list(Group.objects.all().values_list('slug', flat=True))
            self.slug = create_slug(name=self.name, slugs=slugs)
        super(Group, self).save(*args, **kwargs)

    class Meta:
        db_table = 'Group'

    def __str__(self):
        return self.name


class GroupMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True, related_name="groupmember_profile")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name="groupmember_usergroup")
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    approved_by = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True, related_name="groupmember_approvedby")

    class Meta:
        db_table = 'GroupMember'
        unique_together = ('profile', 'group')

    def __str__(self):
        return self.profile.user.username


class GroupRequest(models.Model):
    REQUEST_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True, related_name='grouprequest_profile')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name="grouprequest_usergroup")
    status = models.CharField(max_length=16, choices=REQUEST_CHOICES, default='Pending')
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'GroupRequest'
        unique_together = ('profile', 'group', 'status', 'is_active')

    def __str__(self):
        return self.profile.user.username


class GroupRule(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name="grouprules_group")
    title = models.CharField(max_length=32)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = "GroupRule"

    def __str__(self):
        return self.group.name


class GroupInvite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, related_name='groupinvite_profile')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="groupinvite_group")
    invited_by = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, related_name='groupinvite_invitedby')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'GroupInvite'
        unique_together = ('profile', 'group', 'is_active')

    def __str__(self):
        return self.profile.user.username


class GroupBanner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='groupbanner_group')
    banner = models.ImageField(max_length=255, null=True, blank=True, upload_to='GroupBanners')
    post = models.ForeignKey('youonline_social_app.Post', on_delete=models.CASCADE, null=True, blank=True, related_name="groupbanner_post")
    uploaded_by = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='groupbanner_profile')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)

    class Meta:
        db_table = 'GroupBanner'

    def save(self, *args, **kwargs):
        if self.banner and not self.is_compressed:
            self.banner = s3_compress_image(self.banner)
            self.is_compressed = True
        super(GroupBanner, self).save(*args, **kwargs)


    def __str__(self):
        return self.group.name

class GroupLogo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='grouplogo_group')
    logo = models.ImageField(max_length=255, null=True, blank=True, upload_to='GroupLogo')
    post = models.ForeignKey('youonline_social_app.Post', on_delete=models.CASCADE, null=True, blank=True, related_name="grouplogo_post")
    uploaded_by = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='grouplogo_profile')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)

    class Meta:
        db_table = 'GroupLogo'

    def save(self, *args, **kwargs):
        if self.logo and not self.is_compressed:
            self.logo = s3_compress_image(self.logo)
            self.is_compressed = True
        super(GroupLogo, self).save(*args, **kwargs)


    def __str__(self):
        return self.group.name


class GroupCurrentBanner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    group = models.OneToOneField(Group, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='groupcurrentbanner_group')
    uploaded_by = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='groupcurrentbanner_profile')
    banner = models.OneToOneField(GroupBanner, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='groupcurrentbanner_banner')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'GroupCurrentBanner'

    def __str__(self):
        return self.group.name

class GroupCurrentLogo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    group = models.OneToOneField(Group, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='groupcurrentlogo_group')
    uploaded_by = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='groupcurrentlogo_profile')
    logo = models.OneToOneField(GroupLogo, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='groupcurrentlogo_logo')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'GroupCurrentLogo'

    def __str__(self):
        return self.group.name


# Page Models
class Page(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=32, null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    category = models.ForeignKey(GroupCategory, on_delete=models.CASCADE, null=True, blank=True)
    privacy = models.CharField(max_length=255, choices=YOUONLINE_PRIVACY_CHOICES, default='Public')
    description = models.TextField(null=True, blank=True)
    color = models.CharField(max_length=255, null=True, blank=True)

    username = models.CharField(max_length=255, null=True, blank=True, unique=True)

    # Location
    street_adress = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    invite_with_link = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False)
    is_promoted = models.BooleanField(default=False)
    business_page = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            slugs = list(Page.objects.all().values_list('slug', flat=True))
            self.slug = create_slug(name=self.name, slugs=slugs)
        super(Page, self).save(*args, **kwargs)

    class Meta:
        db_table = 'Page'

    def __str__(self):
        return self.name


class PageFollower(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True, related_name="pagefollower_profile")
    page = models.ForeignKey(Page, on_delete=models.CASCADE, null=True, blank=True, related_name="pagefollower_page")
    is_admin = models.BooleanField(default=False)
    is_administrator = models.BooleanField(default=False)
    is_editor = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    class Meta:
        db_table = 'PageFollower'
        unique_together = ('profile', 'page')

    def make_admin(self):
        self.is_admin = True
        self.is_administrator = False
        self.is_editor = False
        self.save()

    def make_administrator(self):
        self.is_admin = False
        self.is_administrator = True
        self.is_editor = False
        self.save()

    def make_editor(self):
        self.is_admin = False
        self.is_administrator = False
        self.is_editor = True
        self.save()

    def __str__(self):
        return self.profile.user.username


class PageRule(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, null=True, blank=True, related_name="pagerule_page")
    title = models.CharField(max_length=32)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = "PageRule"

    def __str__(self):
        return self.page.name


class PageBanner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='pagebanner_page')
    banner = models.ImageField(max_length=255, null=True, blank=True, upload_to='PageBanners')
    post = models.ForeignKey('youonline_social_app.Post', on_delete=models.CASCADE, null=True, blank=True, related_name="pagebanner_post")
    uploaded_by = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='pagebanner_profile')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)

    class Meta:
        db_table = 'PageBanner'

    def save(self, *args, **kwargs):
        if self.banner and not self.is_compressed:
            self.banner = s3_compress_image(self.banner)
            self.is_compressed = True
        super(PageBanner, self).save(*args, **kwargs)


    def __str__(self):
        return self.page.name

class PageLogo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='pagelogo_page')
    logo = models.ImageField(max_length=255, null=True, blank=True, upload_to='PageLogo')
    post = models.ForeignKey('youonline_social_app.Post', on_delete=models.CASCADE, null=True, blank=True, related_name="pagelogo_post")
    uploaded_by = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='pagelogo_profile')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)

    class Meta:
        db_table = 'PageLogo'

    def save(self, *args, **kwargs):
        if self.logo and not self.is_compressed:
            self.logo = s3_compress_image(self.logo)
            self.is_compressed = True
        super(PageLogo, self).save(*args, **kwargs)


    def __str__(self):
        return self.page.name

class PageInvite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, related_name='pageinvite_profile')
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="pageinvite_page")
    invited_by = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, related_name='pageinvite_invitedby')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'PageInvite'
        unique_together = ('profile', 'page', 'is_active')

    def __str__(self):
        return self.profile.user.username


class PageCurrentBanner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    page = models.OneToOneField(Page, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='pagecurrentbanner_page')
    uploaded_by = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='pagecurrentbanner_profile')
    banner = models.OneToOneField(PageBanner, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='pagecurrentbanner_banner')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'PageCurrentBanner'

    def __str__(self):
        return self.page.name

class PageCurrentLogo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    page = models.OneToOneField(Page, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='pagecurrentlogo_page')
    uploaded_by = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='pagecurrentlogo_profile')
    logo = models.OneToOneField(PageLogo, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='pagecurrentlogo_logo')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'PageCurrentLogo'

    def __str__(self):
        return self.page.name

