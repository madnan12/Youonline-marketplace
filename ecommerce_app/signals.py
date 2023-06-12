# Signals will go here
from django.db.models import signals
from . models import *
from django.conf import settings
import subprocess
from youonline_social_app.constants import upload_to_bucket


def bucket_uploading(sender, instance, signal, *args, **kwargs):
	print("signal called")
	obj = instance
	if sender == BusinessOwner:
		# Upload the files to S3 Bucket
		try:
			if obj.profile_picture:
				upload_to_bucket(obj.profile_picture.path, obj.profile_picture.name)
				subprocess.call("rm " + obj.profile_picture.path, shell=True)
		except Exception as e:
			print("Business Owner Profile Picture upload exception.", e)
			pass
	if sender == ProductMedia:
		# Upload the image to S3 Bucket
		try:
			if obj.image:
				upload_to_bucket(obj.image.path, obj.image.name)
				subprocess.call("rm " + obj.image.path, shell=True)
		except Exception as e:
			print("ProductMedia Image upload exception.", e)
			pass
		# Upload the image thumbnail to S3 Bucket
		try:
			if obj.image_thumbnail:
				upload_to_bucket(obj.image_thumbnail.path, obj.image_thumbnail.name)
				subprocess.call("rm " + obj.image_thumbnail.path, shell=True)
		except Exception as e:
			print("ProductMedia Image thumbnail upload exception.", e)
			pass
		# Upload the video to S3 Bucket
		try:
			if obj.video:
				upload_to_bucket(obj.video.path, obj.video.name)
				subprocess.call("rm " + obj.video.path, shell=True)
		except Exception as e:
			print("ProductMedia Video upload exception.", e)
			pass
		# Upload the video thumbnail to S3 Bucket
		try:
			if obj.video_thumbnail:
				upload_to_bucket(obj.video_thumbnail.path, obj.video_thumbnail.name)
				subprocess.call("rm " + obj.video_thumbnail.path, shell=True)
		except Exception as e:
			print("ProductMedia Video thumbnail upload exception.", e)
			pass


signals.post_save.connect(bucket_uploading, sender=BusinessOwner)
signals.post_save.connect(bucket_uploading, sender=ProductMedia)
