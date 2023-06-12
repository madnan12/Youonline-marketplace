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
from youonline_social_app.models import *


class SendEmailThread(Thread):
    def __init__(self, request, subject, html_template):
        self.request = request
        self.subject = subject
        self.html_template = html_template
        Thread.__init__(self)

    def run(self):
        text_template = strip_tags(self.html_template)
        send_email = EmailMultiAlternatives(
            self.subject,
            text_template,
            settings.EMAIL_HOST_USER,
            [settings.ADMIN_EMAIL]
        )
        send_email.attach_alternative(self.html_template, "text/html")
        try:
            send_email.send(fail_silently=False)
            print("Done")
        except Exception as e:
            print(e)


class RequestSendThread(Thread):
    def __init__(self, request, req_sender, req_receiver):
        self.request = request
        self.req_sender = req_sender
        self.req_receiver = req_receiver
        Thread.__init__(self)

    def run(self):
        try:
            notification_image = UserProfilePicture.objects.get(profile=self.req_sender).picture.picture.url
            notification_image = str(notification_image.replace("/media/", settings.S3_BUCKET_LINK))
        except Exception as e:
            print("Image exception", e)
            notification_image = None
        devices = FCMDevice.objects.filter(device_id=self.req_receiver.id)
        fb_body = {
            'created_at': str(datetime.now()),
            'type': 'FriendRequest',
            'profile': str(self.req_sender.id),
            'receiver_profile': str(self.req_receiver.id),
            'text': f"{self.req_sender.user.first_name} {self.req_sender.user.last_name} sent you friend request.",
        }
        devices.send_message(
            Message(
                data=fb_body,
                notification=FB_Notification(
                    title="Friend Request",
                    body=fb_body['text'],
                    image=notification_image),
        ))


class RequestApproveThread(Thread):
    def __init__(self, request, req_sender, req_receiver):
        self.request = request
        self.req_sender = req_sender
        self.req_receiver = req_receiver
        Thread.__init__(self)

    def run(self):
        try:
            notification_image = UserProfilePicture.objects.get(profile=self.req_receiver).picture.picture.url
        except Exception as e:
            print(e)
            notification_image = None
        devices = FCMDevice.objects.filter(device_id=self.req_sender.id)
        fb_body = {
            'created_at': str(datetime.now()),
            'type': 'AcceptFriendRequest',
            'receiver_profile': str(self.req_receiver.id),
            'sender_profile': str(self.req_receiver.id),
            'text': f"{self.req_receiver.user.first_name} {self.req_receiver.user.last_name} accepted your friend request.",
        }
        devices.send_message(
            Message(
                data=fb_body,
                notification=FB_Notification(
                    title="Accepted Friend Request",
                    body=fb_body['text'],
                    image=notification_image)
        ))


class FollowUserThread(Thread):
    def __init__(self, request, send_profile, rec_profile):
        self.request = request
        self.send_profile = send_profile
        self.rec_profile = rec_profile
        Thread.__init__(self)

    def run(self):
        try:
            notification_image = UserProfilePicture.objects.get(profile=send_profile).picture.picture.url
        except Exception as e:
            print(e)
            notification_image = None
        devices = FCMDevice.objects.filter(device_id=rec_profile.id)
        fb_body = {
            'created_at': str(datetime.now()),
            'type': 'FollowUser',
            'profile': str(send_profile.id),
            'receiver_profile': str(rec_profile.id),
            'text': f"{send_profile.user.first_name} {send_profile.user.last_name} started following you.",
        }
        devices.send_message(
            Message(
                data=fb_body,
                notification=FB_Notification(
                    title="Followed You",
                    body=fb_body['text'],
                    image=notification_image)
        ))


class ReadNotificationsThread(Thread):
    def __init__(self, request, profile, notifications):
        self.request = request
        self.profile = profile
        self.notifications = notifications
        Thread.__init__(self)

    def run(self):
        un_notifications = self.notifications.exclude(read_by=self.profile)
        for noti in un_notifications:
            noti.read_by.add(self.profile)