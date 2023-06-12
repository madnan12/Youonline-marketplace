import uuid
from django.db import models
from youonline_social_app.constants import s3_compress_image, generate_video_thumbnail
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from PIL import Image
import sys
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.storage import default_storage as storage
import random, string
import shutil
from moviepy.editor import VideoFileClip
from django.conf import settings
from youonline_social_app.models import Profile, Post
import tempfile


# Location Module
class Chat(models.Model):
    chat_TYPE = [
        ('Individual', 'Individual'),
        ('Group', 'Group'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=64, null=True, blank=True)
    banner = models.ImageField(upload_to='chat_banners/%Y/%m', null=True, blank=True)
    chat_type = models.CharField(max_length=16, choices=chat_TYPE, default='Individual')
    created_by = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="chat_profile")
    blocked_by = models.ForeignKey(Profile , blank=True, null=True, related_name='block_user_profile', on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    last_message = models.OneToOneField('ChatMessage', on_delete=models.SET_NULL, null=True, blank=True, related_name="chat_lastmessage")
    is_deleted = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        if self.banner:
            self.banner = s3_compress_image(self.banner)
        super(Chat, self).save(*args, **kwargs)

    
    def __str__(self):
        return f"{self.created_by} - {self.created_at}"

    class Meta:
        db_table = "Chat"


class ChatParticipant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True, blank=True, related_name="chatparticipant_chat") # chat_chatparticipant
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="chatparticipant_profile") # profile_chatparticipant
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="chatparticipant_createdby") # createdby_chatparticipant
    deleted_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_muted = models.BooleanField(default=False)
    muted_till = models.DateTimeField(null=True, blank=True)
    removed_by = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="chatparticipant_removedby")
    
    def __str__(self):
        return f"{self.chat.title} - {self.chat.chat_type} - {self.profile.user.username}"

    class Meta:
        db_table = "ChatParticipant"
        unique_together = ('profile', 'chat')


class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True, blank=True, related_name="chatmessage_chat")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name="chatmessage_post")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="chatmessage_profile")
    deleted_by = models.ManyToManyField(Profile, related_name="chatmessage_deletedby", blank=True)
    read_by = models.ManyToManyField(Profile, related_name="chatmessage_readby", blank=True)
    delivered_to = models.ManyToManyField(Profile, related_name='chatmessage_delivered_to' , blank=True)
    text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_forwarded = models.BooleanField(default=False)
    post_message = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)    
    media_message = models.BooleanField(default=False)    
    
    def __str__(self):
        return f"{self.chat.title} - {self.chat.chat_type} - {self.profile.user.username}"

    class Meta:
        db_table = "ChatMessage"


class ChatMessageMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name='chatmessagemedia_profile')
    chat_message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, null=True, blank=True, related_name='chatmessagemedia_chatmessage')

    image = models.ImageField(upload_to='message_images/%Y/%m', max_length=128, null=True)
    image_thumbnail = models.ImageField(upload_to='message_images/%Y/%m', max_length=128, null=True)
    video = models.FileField(upload_to='message_videos/%Y/%m', max_length=128, null=True)
    vid_thumbnail = models.ImageField(upload_to='message_videos/%Y/%m', max_length=128, null=True)
    audio = models.FileField(upload_to='message_audios/%Y/%m', max_length=128, null=True)
    gif = models.CharField(max_length=255, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_compressed = models.BooleanField(default=False)
    video_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def __str__(self):
        return str(self.chat_message)

    def save(self, *args, **kwargs):
        # Compress Image
        if self.image and not self.is_compressed:
            self.image = s3_compress_image(self.image)
            # Create Image Thumbnail
            image_name = str(self.image).split('.')[:-1]
            extension = str(self.image).split('.')[-1]
            image_name = ".".join(image_name)
            image_name = f"{image_name}_thumb.{extension}"
            media_image = Image.open(self.image)
            # copying image to another image object
            media_image.save(f"{settings.MEDIA_ROOT}/{image_name}")
            self.image_thumbnail = image_name
            # Resize image thumbnail to 150 x 150
            thumbnail_picture = Image.open(self.image_thumbnail.path)
            if thumbnail_picture.height > 150 or thumbnail_picture.width > 150:
                # Making it strict to (150, 150) size.
                output_size = (150, 150)
                # We can use resize but to avoid format restrictions, going with thumbnail.
                thumbnail_picture.thumbnail(output_size)
                thumbnail_picture.save(self.image_thumbnail.path, quality=40)
            self.is_compressed = True
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
        super(ChatMessageMedia, self).save(*args, **kwargs)
        

    class Meta:
        db_table = 'ChatMessageMedia'


class ChatDeletionTracker(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True, blank=True, related_name="chatdeletiontracker_chat")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, related_name="chatdeletiontracker_profile")
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ChatDeletionTracker'

    def __str__(self):
        return str(self.id)

