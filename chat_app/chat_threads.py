from threading import Thread
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
from django.core.mail import get_connection, send_mail

from datetime import datetime
from firebase_admin.messaging import Message
from firebase_admin.messaging import Notification as FB_Notification
from fcm_django.models import FCMDevice
from . models import *
from youonline_social_app.models import UserProfilePicture
from youonline_social_app.serializers.post_serializers import DefaultProfileSerializer


class SendMessageThread(Thread):
	def __init__(self, request, chat_message, profile, chat):
		self.request = request
		self.chat_message = chat_message
		self.profile = profile
		self.chat = chat
		Thread.__init__(self)

	def run(self):
		# Create Media List for Chat Message
		media = []
		message_media = ChatMessageMedia.objects.filter(chat_message=self.chat_message)
		if message_media.count() > 0:
			for obj in message_media:
				media_obj = dict()
				if obj.image:
					media_obj['image'] = f"{settings.S3_BUCKET_LINK}{obj.image}"
				if obj.image_thumbnail:
					media_obj['image_thumbnail'] = f"{settings.S3_BUCKET_LINK}{obj.image_thumbnail}"
				if obj.video:
					media_obj['video'] = f"{settings.S3_BUCKET_LINK}{obj.video}"
				if obj.vid_thumbnail:
					media_obj['vid_thumbnail'] = f"{settings.S3_BUCKET_LINK}{obj.vid_thumbnail}"
				if obj.gif:
					media_obj['gif'] = obj.gif
				if obj.audio:
					media_obj['audio'] = f"{settings.S3_BUCKET_LINK}{obj.audio}"
				media.append(media_obj)
		try:
			profile_picture = UserProfilePicture.objects.get(profile=self.chat_message.profile).picture.picture
			profile_picture = f"{settings.S3_BUCKET_LINK}{profile_picture}"
		except Exception as e:
			print("Image exception", e)
			profile_picture = None
		# Send Message to Firestore.
		doc_ref = settings.FIRESTORE.collection(str(self.chat.id)).document(str(self.chat_message.id))
		doc_ref.set({
			u'id': str(self.chat_message.id),
			u'chat': str(self.chat_message.chat.id),
			u'profile': DefaultProfileSerializer(self.chat_message.profile).data,
			u'text': str(self.chat_message.text),
			u'media': media,
			u'created_at': str(self.chat_message.created_at),
			u'deleted_by': [],
			u'deleted_at': str(self.chat_message.deleted_at)
		})
		print("Firestore sent")
		# Firebase Notification For Message
		participants = ChatParticipant.objects.filter(chat=self.chat, is_deleted=False).exclude(profile=self.profile)
		participants_ids = list(participants.values_list('profile__id', flat=True))
		try:
			devices = FCMDevice.objects.filter(device_id__in=participants_ids)
			fb_body = {
				'created_at': str(datetime.now()),
				'type': 'ChatMessage',
				'profile': str(self.profile.id),
				'username': str(self.profile.user.username),
				'first_name': str(self.profile.user.first_name),
				'last_name': str(self.profile.user.last_name),
				'text': str(self.chat_message.text),
				'chat': str(self.chat.id),
			}
			devices.send_message(
			Message(
				data=fb_body,
				notification=FB_Notification(
				title="Chat Message",
				body=fb_body['text'],
				image=profile_picture)
			))
			print("Firebase notification sent")
		except Exception as e:
			print("Firebase exception", e)


class SendPostInMessageThread(Thread):
	def __init__(self, request, chat_message, profile, chat):
		self.request = request
		self.chat_message = chat_message
		self.profile = profile
		self.chat = chat
		Thread.__init__(self)

	def run(self):
		# Get Picture for notification
		try:
			profile_picture = UserProfilePicture.objects.get(profile=self.chat_message.profile).picture.picture
			profile_picture = f"{settings.S3_BUCKET_LINK}{profile_picture}"
		except Exception as e:
			print("Image exception", e)
			profile_picture = None
		# Update firestore for message
		doc_ref = settings.FIRESTORE.collection(str(self.chat.id)).document(str(self.chat_message.id))
		doc_ref.set({
			u'id': str(self.chat_message.id),
			u'chat': str(self.chat_message.chat.id),
			u'profile': DefaultProfileSerializer(self.chat_message.profile).data,
			u'text': str(self.chat_message.text),
			u'media': [],
			u'created_at': str(self.chat_message.created_at),
			u'deleted_at': str(self.chat_message.deleted_at)
		})
		# Firebase Notification For Message
		participants = ChatParticipant.objects.filter(chat=self.chat, is_deleted=False).exclude(profile=self.profile)
		participants_ids = list(participants.values_list('profile__id', flat=True))
		try:
			devices = FCMDevice.objects.filter(device_id__in=participants_ids)
			fb_body = {
				'created_at': str(datetime.datetime.now()),
				'type': 'ChatMessage',
				'profile': str(self.profile.id),
				'username': str(self.profile.user.username),
				'first_name': str(self.profile.user.first_name),
				'last_name': str(self.profile.user.last_name),
				'text': str(self.chat_message.text),
				'chat': str(self.chat.id),
			}
			devices.send_message(
			Message(
				data=fb_body,
				notification=FB_Notification(
				title="Chat Message",
				body=fb_body['text'],
				image=profile_picture)
			))
		except Exception as e:
			print("Firebase exception", e)


class ForwardChatMessageThread(Thread):
	def __init__(self, request, forward_message, profile, chat):
		self.request = request
		self.forward_message = forward_message
		self.profile = profile
		self.chat = chat
		Thread.__init__(self)

	def run(self):
		# Getting profile picture
		try:
			profile_picture = UserProfilePicture.objects.get(profile=self.forward_message.profile).picture.picture
			profile_picture = f"{settings.S3_BUCKET_LINK}{profile_picture}"
		except Exception as e:
			print("Image exception", e)
			profile_picture = None
		# Create Media Dictionary for Forward Message.
		media = []
		message_media = ChatMessageMedia.objects.filter(chat_message=self.forward_message)
		if message_media.count() > 0:
			for obj in message_media:
				media_obj = dict()
				if obj.image:
					media_obj['image'] = f"{settings.S3_BUCKET_LINK}{self.obj.image}"
				if obj.image_thumbnail:
					media_obj['image_thumbnail'] = f"{settings.S3_BUCKET_LINK}{self.obj.image_thumbnail}"
				if obj.video:
					media_obj['video'] = f"{settings.S3_BUCKET_LINK}{self.obj.video}"
				if obj.vid_thumbnail:
					media_obj['vid_thumbnail'] = f"{settings.S3_BUCKET_LINK}{self.obj.vid_thumbnail}"
				if obj.gif:
					media_obj['gif'] = self.obj.gif
				if obj.audio:
					media_obj['audio'] = f"{settings.S3_BUCKET_LINK}{self.obj.audio}"
				media.append(media_obj)
		# Send Forward Message to Firestore.
		doc_ref = settings.FIRESTORE.collection(str(self.chat.id)).document(str(self.forward_message.id))
		doc_ref.set({
			u'id': str(self.forward_message.id),
			u'chat': str(self.forward_message.chat.id),
			u'profile': DefaultProfileSerializer(self.forward_message.profile).data,
			u'text': str(self.forward_message.text),
			u'media': media,
			u'is_forwarded': 'true',
			u'created_at': str(self.forward_message.created_at),
			u'deleted_by': [],
			u'deleted_at': str(self.forward_message.deleted_at)
		})
		# Firebase Notification For Message
		participants = ChatParticipant.objects.filter(chat=self.chat, is_deleted=False).exclude(profile=self.profile)
		participants_ids = list(participants.values_list('profile__id', flat=True))
		try:
			devices = FCMDevice.objects.filter(device_id__in=participants_ids)
			fb_body = {
				'created_at': str(datetime.now()),
				'type': 'ChatMessage',
				'profile': str(self.profile.id),
				'username': str(self.profile.user.username),
				'first_name': str(self.profile.user.first_name),
				'last_name': str(self.profile.user.last_name),
				'text': str(self.forward_message.text),
				'chat': str(self.chat.id),
			}
			devices.send_message(
				Message(
					data=fb_body,
					notification=FB_Notification(
					title="Chat Message",
					body=fb_body['text'],
					image=profile_picture)
				))

		except Exception as e:
			print("Firebase exception in forward message", e)
