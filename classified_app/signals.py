from django.db.models import signals
from . models import ClassifiedMedia
from django.conf import settings
import random, string, subprocess
from youonline_social_app.constants import upload_to_bucket
 

def compress_video(sender, instance, signal, *args, **kwargs):
    obj = instance
    try:
        if obj.classified_video and not obj.video_compressed:
            if obj.classified_video.size > 3011022:
                input = f"{settings.MEDIA_ROOT}/{obj.classified_video}"
                output = input.split('.')[:-1]
                extension = input.split('.')[-1]
                random_digits_for_video = ''.join(
                    random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
                output = f"{output[0]}{random_digits_for_video}_compressed.{extension}"
                proc = subprocess.call("ffmpeg -i " + input + " -vcodec libx264 -crf 32 " + output, shell=True)
                print("Compression done.")
                obj.classified_video.delete()
                output = output.split('media')[-1]
                output = output[1:]
                obj.classified_video = output
                obj.video_compressed = True
                obj.save()
            else:
                obj.video_compressed = True
                obj.save()
                print("No compression is done for small video.")
        # Upload the files to S3 Bucket
        if not obj.bucket_uploaded:
            if obj.classified_video:
                upload_to_bucket(obj.classified_video.path, obj.classified_video.name)
                subprocess.call("rm -f " + obj.classified_video.path, shell=True)
                if obj.classified_video_thumbnail:
                    upload_to_bucket(obj.classified_video_thumbnail.path, obj.classified_video_thumbnail.name)
                    subprocess.call("rm " + obj.classified_video_thumbnail.path, shell=True)
                obj.bucket_uploaded = True
                obj.save()
            if obj.classified_image:
                upload_to_bucket(obj.classified_image.path, obj.classified_image.name)
                subprocess.call("rm " + obj.classified_image.path, shell=True)
                obj.bucket_uploaded = True
                obj.save()
    except Exception as e:
        print(e)
        obj.delete()


signals.post_save.connect(compress_video, sender=ClassifiedMedia)
