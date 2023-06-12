import uuid
from django.db import models
from youonline_social_app.constants import s3_compress_image
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
import tempfile


# Create your models here.
YOUONLINE_PRIVACY_CHOICES = [
        ('Public', 'Public'),
        ('OnlyMe', 'OnlyMe'),
        ('Friends', 'Friends'),
    ]


class VideoChannel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="channel_profile")
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_compressed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # create Slug for video channel name
        slugs = list(VideoChannel.objects.all().values_list('slug', flat=True))
        self.slug = create_slug(name=self.name, slugs=slugs)
        super(VideoChannel, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'VideoChannel'


class ChannelPicture(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    channel = models.OneToOneField(VideoChannel, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='channelpicture_channel')
    picture = models.ImageField(max_length=255, upload_to="YoutubePicture", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)

    class Meta:
        db_table = 'ChannelPicture'

    def save(self, *args, **kwargs):
        if self.picture and not self.is_compressed:
            self.picture = s3_compress_image(self.picture)
            self.is_compressed = True
        super(ChannelPicture, self).save(*args, **kwargs)


    def __str__(self):
        return self.channel.name


class ChannelCover(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    channel = models.OneToOneField(VideoChannel, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='channelcover_channel')
    cover = models.ImageField(max_length=255, upload_to="YoutubeCover", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)

    class Meta:
        db_table = 'ChannelCover'

    def save(self, *args, **kwargs):
        if self.cover and not self.is_compressed:
            self.cover = s3_compress_image(self.cover)
            self.is_compressed = True
        super(ChannelCover, self).save(*args, **kwargs)


    def __str__(self):
        return self.channel.name


class VideoPlaylist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    channel = models.ForeignKey(VideoChannel, on_delete=models.CASCADE, related_name="playlist_channel")
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    description = models.TextField(null=True, blank=True)
    privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default='Public', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Create Slug for Video Playlist
        slugs = list(VideoPlaylist.objects.all().values_list('slug', flat=True))
        self.slug = create_slug(name=self.name, slugs=slugs)
        super(VideoPlaylist, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('channel', 'name')
        db_table = 'VideoPlaylist'


class PlaylistBanner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    playlist = models.OneToOneField(VideoPlaylist, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='playlistbanner_playlist')
    banner = models.ImageField(max_length=255, null=True, blank=True, upload_to='PlaylistBanners')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)

    class Meta:
        db_table = 'PlaylistBanner'

    def save(self, *args, **kwargs):
        if self.banner and not self.is_compressed:
            self.banner = s3_compress_image(self.banner)
            self.is_compressed = True
        super(PlaylistBanner, self).save(*args, **kwargs)


    def __str__(self):
        return self.playlist.name


class VideoCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=32)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "VideoCategory"


class VideoSubCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    category = models.ForeignKey(VideoCategory, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=32)

    def __str__(self):
        if self.category:
            return f"{self.title} - {self.category.title}"
        else:
            return self.title

    class Meta:
        db_table = "VideoSubCategory"


class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="video_profile")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name="videomodule_post")
    channel = models.ForeignKey(VideoChannel, on_delete=models.CASCADE, null=True, blank=True, related_name="video_channel")
    privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default='Public', null=True, blank=True)
    title = models.CharField(max_length=128, null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    short_description = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    video = models.FileField(upload_to='videos_module/%Y/%m', max_length=256, null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    vid_thumbnail = models.FileField(upload_to='videos_module/%Y/%m', max_length=256, null=True, blank=True)
    youtube_link = models.CharField(max_length=128, null=True, blank=True)
    category = models.ForeignKey(VideoCategory, on_delete=models.CASCADE, null=True, blank=True)
    sub_category = models.ForeignKey(VideoSubCategory, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    inactive_video = models.BooleanField(default=False)
    total_views = models.BigIntegerField(default=0)
    video_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Generate Slug
        if not self.slug:
            slugs = list(Video.objects.all().values_list('slug', flat=True))
            self.slug = create_slug(title=self.title, slugs=slugs)
        # Generate Video Thumnail
        if self.video and not self.vid_thumbnail:
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
            self.duration = int(clip.duration)
        super(Video, self).save(*args, **kwargs)
        
    def __str__(self):
        return self.profile.user.username

    class Meta:
        db_table = 'Video'


class VideoWatchLater(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="videowatchlater_profile")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, null=True, blank=True, related_name="videowatchlater_video")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.profile.user.username

    class Meta:
        unique_together = ('video', 'profile')
        db_table = 'VideoWatchLater'
        

class VideoWatched(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="videowatched_profile")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, null=True, blank=True, related_name="videowatched_video")
    times_watched = models.BigIntegerField(default=0)
    last_watched = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.profile.user.username

    class Meta:
        db_table = 'VideoWatched'


class VideoPlaylistPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    playlist = models.ForeignKey(VideoPlaylist, on_delete=models.CASCADE, null=True, blank=True, related_name="videoplaylistpost_playlist")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name="videoplaylistpost_post")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        unique_together = ('playlist', 'post')
        db_table = 'VideoPlaylistPost'


class VideoChannelSubscribe(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="videochannelsubscribe_profile")
    channel = models.ForeignKey(VideoChannel, on_delete=models.CASCADE, null=True, blank=True, related_name="videochannelsubscribe_channel")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        unique_together = ('profile', 'channel')
        db_table = 'VideoChannelSubscribe'


