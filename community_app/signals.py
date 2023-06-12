from django.db.models import signals
from . models import GroupBanner, GroupLogo, PageBanner, PageLogo
from moviepy import *
from django.conf import settings
import random, string, subprocess
from youonline_social_app.constants import upload_to_bucket
   

def bucket_upload_signal(sender, instance, signal, *args, **kwargs):
    if sender == PageBanner:
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
            obj.post.delete()
    elif sender == GroupBanner:
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
            obj.post.delete()
    elif sender == GroupLogo:
        obj = instance
        # Upload the files to S3 Bucket
        try:
            if not obj.bucket_uploaded:
                if obj.logo:
                    upload_to_bucket(obj.logo.path, obj.logo.name)
                    subprocess.call("rm " + obj.logo.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
        except Exception as e:
            print(e)
            obj.post.delete()
    elif sender == PageLogo:
        obj = instance
        # Upload the files to S3 Bucket
        try:
            if not obj.bucket_uploaded:
                if obj.logo:
                    upload_to_bucket(obj.logo.path, obj.logo.name)
                    subprocess.call("rm " + obj.logo.path, shell=True)
                    obj.bucket_uploaded = True
                    obj.save()
        except Exception as e:
            print(e)
            obj.post.delete()

signals.post_save.connect(bucket_upload_signal, sender=PageBanner)
signals.post_save.connect(bucket_upload_signal, sender=PageLogo)
signals.post_save.connect(bucket_upload_signal, sender=GroupBanner)
signals.post_save.connect(bucket_upload_signal, sender=GroupLogo)