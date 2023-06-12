from django.db.models import signals
from . models import JobApplyMedia, JobMedia, JobProjectMedia, JobStory, CompanyLogo, CompanyCoverImage
from django.conf import settings
import random, string, subprocess
from youonline_social_app.constants import upload_to_bucket
 

def compress_video(sender, instance, signal, *args, **kwargs):
    obj = instance
    if sender == JobProjectMedia:
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
    obj = instance
    if sender == JobStory:
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

    obj = instance
    if sender == JobMedia:
        if obj.job_video and not obj.video_compressed:
            if obj.job_video.size > 3011022:
                input = f"{settings.MEDIA_ROOT}/{obj.job_video}"
                output = input.split('.')[:-1]
                extension = input.split('.')[-1]
                random_digits_for_video = ''.join(
                    random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
                output = f"{output[0]}{random_digits_for_video}_compressed.{extension}"
                proc = subprocess.call("ffmpeg -i " + input + " -vcodec libx264 -crf 32 " + output, shell=True)
                print("Compression done.")
                obj.job_video.delete()
                output = output.split('media')[-1]
                output = output[1:]
                obj.job_video = output
                obj.video_compressed = True
                obj.save()
            else:
                obj.video_compressed = True
                obj.save()
                print("No compression is done for small video.")
        # Upload the files to S3 Bucket
        if not obj.bucket_uploaded:
            if obj.job_video:
                upload_to_bucket(obj.job_video.path, obj.job_video.name)
                subprocess.call("rm -f " + obj.job_video.path, shell=True)
                if obj.vid_thumbnail:
                    upload_to_bucket(obj.vid_thumbnail.path, obj.vid_thumbnail.name)
                    subprocess.call("rm " + obj.vid_thumbnail.path, shell=True)
                obj.bucket_uploaded = True
                obj.save()
            if obj.job_image:
                upload_to_bucket(obj.job_image.path, obj.job_image.name)
                subprocess.call("rm " + obj.job_image.path, shell=True)
                obj.bucket_uploaded = True
                obj.save()

    obj = instance
    if sender == CompanyLogo:
        if not obj.bucket_uploaded:
            if obj.logo:
                upload_to_bucket(obj.logo.path, obj.logo.name)
                subprocess.call("rm " + obj.logo.path, shell=True)
                obj.bucket_uploaded = True
                obj.save()
                print('signal called')
                
    obj = instance
    if sender == CompanyCoverImage:
        if not obj.bucket_uploaded:
            if obj.cover_image:
                upload_to_bucket(obj.cover_image.path, obj.cover_image.name)
                subprocess.call("rm " + obj.cover_image.path, shell=True)
                obj.bucket_uploaded = True
                obj.save()
                print('signal called')

    obj = instance
    if sender == JobApplyMedia:
        if not obj.bucket_uploaded:
            if obj.resume_file:
                upload_to_bucket(obj.resume_file.path, obj.resume_file.name)
                obj.bucket_uploaded = True
                obj.save()
                print('signal called')

signals.post_save.connect(compress_video, sender=JobProjectMedia)
signals.post_save.connect(compress_video, sender=JobStory)
signals.post_save.connect(compress_video, sender=JobMedia)
signals.post_save.connect(compress_video, sender=CompanyLogo)
signals.post_save.connect(compress_video, sender=CompanyCoverImage)
signals.post_save.connect(compress_video, sender=JobApplyMedia)
