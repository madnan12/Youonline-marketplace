from concurrent.futures import thread
from threading import Thread
from django.db.models import signals
from . models import CompanyMedia, PostMedia, UserAlbumMedia, CommentMedia,\
                    CommentReplyMedia, ProfileStory, CoverPicture, ProfilePicture, Notification
from moviepy import *
from django.conf import settings
import random, string, subprocess
from . constants import upload_to_bucket
from django.dispatch import receiver

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class VideoCompressionAndUploadThread(Thread):
    def __init__(self, obj):
        self.obj = obj
        Thread.__init__(self)

    
    def run(self):
        print('Compression Thread')
        if self.obj.post_video and not self.obj.video_compressed:
            if self.obj.post_video.size > 3011022:
                print("Compression starts")
                # Get the video path
                input = f"{settings.MEDIA_ROOT}/{self.obj.post_video}"
                # Get the name of the video
                video_path = self.obj.post_video.path
                video_name = self.obj.post_video.name
                output = input.split('.')[:-1]
                extension = input.split('.')[-1]
                # Create a temporary name for video
                random_digits_for_video = ''.join(
                    random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
                output = f"{output[0]}{random_digits_for_video}_compressed.{extension}"
                proc = subprocess.call("ffmpeg -i " + input + " -vcodec libx264 -crf 32 " + output, shell=True)
                print("Compression done.")
                self.obj.post_video.delete()
                output = output.split('media')[-1]
                output = output[1:]
                self.obj.post_video = output
                self.obj.video_compressed = True
                # Rename the video and upload it to the bucket.
                print("uploading to bucket and remove the remaining file")
                output = f"{settings.MEDIA_ROOT}/{output}"
                subprocess.call("mv  " + output + " " + video_path, shell=True)
                print("Renaming done")
                upload_to_bucket(video_path, video_name)
                print("Uploading to bucket done")
                subprocess.call("rm -f " + video_path, shell=True)
                print("Removing file done")
                self.obj.save()
                # Rename the object
            else:
                self.obj.video_compressed = True
                self.obj.save()
                print("No compression is done for small video.")

 

def compress_video(sender, instance, signal, *args, **kwargs):
    if sender == PostMedia:
        obj = instance
        try:
            VideoCompressionAndUploadThread(obj).start()
            # Upload the files to S3 Bucket
            if not obj.bucket_uploaded:
                if obj.post_video:
                    upload_to_bucket(obj.post_video.path, obj.post_video.name)
                    subprocess.call("rm -f " + obj.post_video.path, shell=True)
                    if obj.vid_thumbnail:
                        upload_to_bucket(obj.vid_thumbnail.path, obj.vid_thumbnail.name)
                        subprocess.call("rm " + obj.vid_thumbnail.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
                if obj.post_image:
                    upload_to_bucket(obj.post_image.path, obj.post_image.name)
                    subprocess.call("rm " + obj.post_image.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
                if obj.post_audio:
                    upload_to_bucket(obj.post_audio.path, obj.post_audio.name)
                    subprocess.call("rm " + obj.post_audio.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
                if obj.background_image:
                    upload_to_bucket(obj.background_image.path, obj.background_image.name)
                    subprocess.call("rm " + obj.background_image.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
        except Exception as e:
            print(e)

    elif sender == UserAlbumMedia:
        obj = instance
        try:
            if obj.video and not obj.video_compressed:
                if obj.video.size > 3011022:
                    input = f"{settings.MEDIA_ROOT}/{obj.video}"
                    output = input.split('.')[:-1]
                    extension = input.split('.')[-1]
                    random_digits_for_video = ''.join(
                        random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
                    output = f"{output[0]}{random_digits_for_video}_compressed.{extension}"
                    proc = subprocess.call("ffmpeg -i " + input + " -vcodec libx264 -crf 32 " + output, shell=True)
                    print("Compression done.")
                    obj.video.delete()
                    output = output.split('media')[-1]
                    output = output[1:]
                    obj.video = output
                    obj.video_compressed = True
                    obj.save()
                else:
                    obj.video_compressed = True
                    obj.save()
                    print("No compression is done for small video.")
            # Upload the files to S3 Bucket
            if not obj.bucket_uploaded:
                if obj.video:
                    upload_to_bucket(obj.video.path, obj.video.name)
                    subprocess.call("rm -f " + obj.video.path, shell=True)
                    if obj.vid_thumbnail:
                        upload_to_bucket(obj.vid_thumbnail.path, obj.vid_thumbnail.name)
                        subprocess.call("rm " + obj.vid_thumbnail.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
                if obj.image:
                    upload_to_bucket(obj.image.path, obj.image.name)
                    subprocess.call("rm " + obj.image.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
        except Exception as e:
            print(e)
    elif sender == CommentMedia:
        obj = instance
        try:
            if obj.comment_video and not obj.video_compressed:
                if obj.comment_video.size > 3011022:
                    input = f"{settings.MEDIA_ROOT}/{obj.comment_video}"
                    output = input.split('.')[:-1]
                    extension = input.split('.')[-1]
                    random_digits_for_video = ''.join(
                        random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
                    output = f"{output[0]}{random_digits_for_video}_compressed.{extension}"
                    proc = subprocess.call("ffmpeg -i " + input + " -vcodec libx264 -crf 32 " + output, shell=True)
                    print("Compression done.")
                    obj.comment_video.delete()
                    output = output.split('media')[-1]
                    output = output[1:]
                    obj.comment_video = output
                    obj.video_compressed = True
                    obj.save()
                else:
                    obj.video_compressed = True
                    obj.save()
                    print("No compression is done for small video.")
            # Upload the files to S3 Bucket
            if not obj.bucket_uploaded:
                if obj.comment_video:
                    upload_to_bucket(obj.comment_video.path, obj.comment_video.name)
                    subprocess.call("rm -f " + obj.comment_video.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
                if obj.comment_image:
                    upload_to_bucket(obj.comment_image.path, obj.comment_image.name)
                    subprocess.call("rm " + obj.comment_image.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
                if obj.comment_audio:
                    upload_to_bucket(obj.comment_audio.path, obj.comment_audio.name)
                    subprocess.call("rm " + obj.comment_audio.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
        except Exception as e:
            print(e)

    elif sender == CommentReplyMedia:
        obj = instance
        try:
            if obj.reply_video and not obj.video_compressed:
                if obj.reply_video.size > 3011022:
                    input = f"{settings.MEDIA_ROOT}/{obj.reply_video}"
                    output = input.split('.')[:-1]
                    extension = input.split('.')[-1]
                    random_digits_for_video = ''.join(
                        random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
                    output = f"{output[0]}{random_digits_for_video}_compressed.{extension}"
                    proc = subprocess.call("ffmpeg -i " + input + " -vcodec libx264 -crf 32 " + output, shell=True)
                    print("Compression done.")
                    obj.reply_video.delete()
                    output = output.split('media')[-1]
                    output = output[1:]
                    obj.reply_video = output
                    obj.video_compressed = True
                    obj.save()
                else:
                    obj.video_compressed = True
                    obj.save()
                    print("No compression is done for small video.")
            # Upload the files to S3 Bucket
            if not obj.bucket_uploaded:
                if obj.reply_video:
                    upload_to_bucket(obj.reply_video.path, obj.reply_video.name)
                    subprocess.call("rm -f " + obj.reply_video.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
                if obj.reply_image:
                    upload_to_bucket(obj.reply_image.path, obj.reply_image.name)
                    subprocess.call("rm " + obj.reply_image.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
                if obj.reply_audio:
                    upload_to_bucket(obj.reply_audio.path, obj.reply_audio.name)
                    subprocess.call("rm " + obj.reply_audio.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
        except Exception as e:
            print(e)
    elif sender == ProfileStory:
        obj = instance
        try:
            if obj.media_video and not obj.video_compressed:
                if obj.media_video.size > 3011022:
                    input = f"{settings.MEDIA_ROOT}/{obj.media_video}"
                    output = input.split('.')[:-1]
                    extension = input.split('.')[-1]
                    random_digits_for_video = ''.join(
                        random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
                    output = f"{output[0]}{random_digits_for_video}_compressed.{extension}"
                    proc = subprocess.call("ffmpeg -i " + input + " -vcodec libx264 -crf 32 " + output, shell=True)
                    print("Compression done.")
                    obj.media_video.delete()
                    output = output.split('media')[-1]
                    output = output[1:]
                    obj.media_video = output
                    obj.video_compressed = True
                    obj.save()
                else:
                    obj.video_compressed = True
                    obj.save()
                    print("No compression is done for small video.")
            # Upload the files to S3 Bucket
            if not obj.bucket_uploaded:
                if obj.media_video:
                    upload_to_bucket(obj.media_video.path, obj.media_video.name)
                    subprocess.call("rm -f " + obj.media_video.path, shell=True)
                    if obj.video_thumbnail:
                        upload_to_bucket(obj.video_thumbnail.path, obj.video_thumbnail.name)
                        subprocess.call("rm " + obj.video_thumbnail.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
                if obj.media_image:
                    upload_to_bucket(obj.media_image.path, obj.media_image.name)
                    subprocess.call("rm " + obj.media_image.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
        except Exception as e:
            print(e)


def bucket_upload_signal(sender, instance, signal, *args, **kwargs):
    if sender == ProfilePicture:
        obj = instance
        # Upload the files to S3 Bucket
        try:
            if not obj.bucket_uploaded:
                if obj.picture:
                    upload_to_bucket(obj.picture.path, obj.picture.name)
                    subprocess.call("rm " + obj.picture.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
        except Exception as e:
            print(e)
    elif sender == CoverPicture:
        obj = instance
        # Upload the files to S3 Bucket
        try:
            if not obj.bucket_uploaded:
                if obj.cover:
                    upload_to_bucket(obj.cover.path, obj.cover.name)
                    subprocess.call("rm " + obj.cover.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
        except Exception as e:
            print(e)
    elif sender == CompanyMedia:
        obj = instance
        try:
            if not obj.bucket_uploaded:
                if obj.logo:
                    upload_to_bucket(obj.logo.path, obj.logo.name)
                    subprocess.call("rm " + obj.logo.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
        except Exception as e:
            print(e)

signals.post_save.connect(compress_video, sender=PostMedia)
signals.post_save.connect(compress_video, sender=UserAlbumMedia)
signals.post_save.connect(compress_video, sender=CommentMedia)
signals.post_save.connect(compress_video, sender=CommentReplyMedia)
signals.post_save.connect(compress_video, sender=ProfileStory)
signals.post_save.connect(bucket_upload_signal, sender=ProfilePicture)
signals.post_save.connect(bucket_upload_signal, sender=CoverPicture)
signals.post_save.connect(bucket_upload_signal, sender=CompanyMedia)
