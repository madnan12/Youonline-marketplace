from django.db.models import signals
from . models import BlogMedia, BlogAuthor
from django.conf import settings
import random, string, subprocess
from youonline_social_app.constants import upload_to_bucket
 
# upload to Bucket
def bucket_upload_signal(sender, instance, signal, *args, **kwargs):
    if sender == BlogMedia:
        obj = instance
        # Upload the files to S3 Bucket
        try:
            if not obj.bucket_uploaded:
                if obj.featured_image:
                    upload_to_bucket(obj.featured_image.path, obj.featured_image.name)
                    subprocess.call("rm " + obj.featured_image.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
        except Exception as e:
            print(e)
            obj.delete()
    elif sender == BlogAuthor:
        obj = instance
        # Upload the files to S3 Bucket
        try:
            if not obj.bucket_uploaded:
                if obj.resume:
                    upload_to_bucket(obj.resume.path, obj.resume.name)
                    obj.bucket_uploaded = True
                    obj.save()
        except Exception as e:
            print(e)
            obj.delete()
signals.post_save.connect(bucket_upload_signal, sender=BlogMedia)
signals.post_save.connect(bucket_upload_signal, sender=BlogAuthor)