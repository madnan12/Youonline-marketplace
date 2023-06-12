from django.db.models import signals
from . models import Video, ChannelPicture, ChannelCover, PlaylistBanner
from django.conf import settings
import random, string, subprocess
from youonline_social_app.constants import upload_to_bucket
 

def compress_video(sender, instance, signal, *args, **kwargs):
    obj = instance
    try:
        if obj.video and not obj.video_compressed:
            if obj.video.size > 3011022:
                input = f"{settings.MEDIA_ROOT}/{obj.video}"
                output = input.split('.')[:-1]
                extension = input.split('.')[-1]
                random_digits_for_video = ''.join(
                    random.SystemRandom().choice(string.hexdigits + string.hexdigits) for _ in range(10))
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
    except Exception as e:
        print(e)
    

def bucket_upload_signal(sender, instance, signal, *args, **kwargs):
    # Signal For Channel Picture
    if sender == ChannelPicture:
        try:
            obj = instance
            # Upload the files to S3 Bucket
            if not obj.bucket_uploaded:
                if obj.picture:
                    upload_to_bucket(obj.picture.path, obj.picture.name)
                    subprocess.call("rm " + obj.picture.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
        except Exception as e:
            print(e)
    # Signal For ChannelCover
    elif sender == ChannelCover:
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
    # Signal For Playlist Banner
    elif sender == PlaylistBanner:
        obj = instance
        # Upload the files to S3 Bucket
        try:
            if not obj.bucket_uploaded:
                if obj.banner:
                    upload_to_bucket(obj.banner.path, obj.banner.name)
                    subprocess.call("rm " + obj.banner.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
        except Exception as e:
            print(e)


signals.post_save.connect(compress_video, sender=Video)
signals.post_save.connect(bucket_upload_signal, sender=ChannelPicture)
signals.post_save.connect(bucket_upload_signal, sender=ChannelCover)
signals.post_save.connect(bucket_upload_signal, sender=PlaylistBanner)
