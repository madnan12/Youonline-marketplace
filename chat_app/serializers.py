import datetime
from attr import field
from rest_framework import serializers
from . models import *
import random, string
from rest_framework import status
from . import views
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
from moviepy.editor import VideoFileClip
from youonline_social_app.serializers.post_serializers import *
from fcm_django.models import FCMDevice
from youonline_social_app.serialized_methods import *


class ChatMessageSerializer(serializers.ModelSerializer):
    image = serializers.ListField(required=False, allow_null=True,
                                       child=serializers.FileField(
                                           max_length=1000000, allow_empty_file=True, use_url=False
                                       ))
    video = serializers.ListField(required=False, allow_null=True,
                                       child=serializers.FileField(
                                           max_length=1000000, allow_empty_file=True, use_url=False
                                       ))
    audio = serializers.ListField(required=False, allow_null=True,
                                       child=serializers.FileField(
                                           max_length=1000000, allow_empty_file=True, use_url=False
                                       ))
    gif = serializers.ListField(required=False, allow_null=True,
                                     child=serializers.CharField(max_length=255, allow_blank=True, trim_whitespace=False))
    class Meta:
        model = ChatMessage
        fields = '__all__'

    def create(self, validated_data):
        """
        Override the create method to add custom validation
        - Create a post with every property creation.
        - Validate media formats.
        - Create ChatMessageMedia objects with every media.
        """
        try:
            use = validated_data.pop('profile')
            try:
                user = Profile.objects.get(id=use.id)
            except ObjectDoesNotExist:
                print("Error here.")
                error = serializers.ValidationError(
                    {'success': False, 'response': {'message': 'User does not exist'}})
                error.status_code = 404
                raise error
        except:
            error = serializers.ValidationError(
                {'success': False, 'response': {'message': 'Please, Enter User ID'}})
            error.status_code = 400
            raise error
        try:
            text = validated_data.pop('text')
        except:
            text = None
        try:
            chat = validated_data.pop('chat')
            try:
                chat = Chat.objects.get(id=chat.id)
            except Exception as e:
                print("Exception occured here.")
                error = serializers.ValidationError(
                    {'success': False, 'response': {'message': str(e)}})
                error.status_code = 404
                raise error
        except Exception as e:
            error = serializers.ValidationError(
                    {'success': False, 'response': {'message': str(e)}})
            error.status_code = 404
            raise error
        chat_message = ChatMessage(
            chat=chat,
            profile=user,
            text=text
        )
        chat_message.save()
        try:
            image = validated_data.pop('image')
        except:
            image = None
        try:
            audio = validated_data.pop('audio')
        except:
            audio = None
        try:
            gif = validated_data.pop('gif')
        except:
            gif = None
        try:
            video = validated_data['video']
        except:
            video = None
        if image is not None:
            for i in image:
                name = i.name.split('.')
                if name[-1].strip() in ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG']:
                    med_obj = ChatMessageMedia(
                        profile=user,
                        chat_message=chat_message,
                        image=i
                    )
                    med_obj.save()
                else:
                    chat_message.delete()
                    raise serializers.ValidationError({'success': False,
                                                         'response': {
                                                             'message': 'Error in Image field,'
                                                                        'Only these formats are allowed {}'.format(
                                                                 ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG'])}})
            chat_message.media_message = True
            chat_message.save()
        if audio is not None:
            for i in audio:
                name = i.name.split('.')
                if name[-1] in ['mp3', 'MP3']:
                    chatmedia = ChatMessageMedia(
                        profile=user,
                        chat_message=chat_message,
                        audio=i
                    )
                    chatmedia.save()
                else:
                    chat_message.delete()
                    raise serializers.ValidationError({'success': False,
                                                         'response': {
                                                             'message': 'Error in Audio field,'
                                                                        'Only these formats are allowed {}'.format(
                                                                 ['mp3', 'MP3'])}})
            chat_message.media_message = True
            chat_message.save()
        if gif is not None:
            for i in gif:
                chatmedia = ChatMessageMedia(
                    profile=user,
                    chat_message=chat_message,
                    gif=i
                )
                chatmedia.save()
            chat_message.media_message = True
            chat_message.save()
        if video is not None:
            for i in video:
                name = i.name.split('.')
                if name[-1] in ['mp4', 'mkv', 'webm', 'avi', 'flv', 'wmv', 'mov', 'MP4', 'MKV', 'WEBM', 'AVI', 'FLV', 'WMV', 'MOV']:
                    if i.size > 75000000:
                        chat_message.delete()
                        error = serializers.ValidationError({'success': False,
                                                             'response': {
                                                                 'message': 'Error in Video size. Maximum allowed size is 75mb.'}})
                        error.status_code = 400
                        raise error
                    else:
                        obj = ChatMessageMedia(
                                profile=user,
                                chat_message=chat_message,
                                video=i
                            )
                        obj.save()
                        # create_post.delay(obj.id)
                else:
                    chat_message.delete()
                    raise serializers.ValidationError({'success': False,
                                                         'response': {
                                                             'message': 'Error in Video field,'
                                                                        'Only these formats are allowed {}'.format(
                                                                 ['mp4', 'mkv', 'webm', 'avi', 'flv', 'wmv', 'mov', 'MP4', 'MKV', 'WEBM', 'AVI', 'FLV', 'WMV', 'MOV'])}})
            chat_message.media_message = True
            chat_message.save()
        return chat_message


class GetChatMessageMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessageMedia
        fields = ('image', 'video', 'audio', 'gif')

    def to_representation(self, obj):
        return_dict = {}
        if obj.image:
            return_dict['image'] = f"{settings.S3_BUCKET_LINK}{obj.image}"
            return_dict['id'] = obj.id
        if obj.video:
            return_dict['video'] = f"{settings.S3_BUCKET_LINK}{obj.video}"
            if obj.vid_thumbnail:
                return_dict['video_thumbnail'] = f"{settings.S3_BUCKET_LINK}{obj.vid_thumbnail}"
            else:
                return_dict['video_thumbnail'] = ''
            return_dict['id'] = obj.id
        if obj.audio:
            return_dict['audio'] = f"{settings.S3_BUCKET_LINK}{obj.audio}"
            return_dict['id'] = obj.id
        if obj.gif:
            return_dict['gif'] = obj.gif
            return_dict['id'] = obj.id

        return return_dict


class GetChatMessageSerializer(serializers.ModelSerializer):
    profile = DefaultProfileSerializer()
    media = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()
    deleted_by = serializers.SerializerMethodField()
    delivered_to = serializers.SerializerMethodField()
    

    def get_media(self, chat_message):
        if chat_message.media_message:
            return GetChatMessageMediaSerializer(chat_message.chatmessagemedia_chatmessage.filter(is_deleted=False), many=True).data
        else:
            return None

    def get_post(self, chat_message):
        if chat_message.post_message:
            try:
                return PostGetSerializer(chat_message.post).data
            except:
                return None
        else:
            return None

    def get_delivered_to(self, chat_message):
        all_profiles = chat_message.delivered_to.all()
        return DefaultProfileSerializer(all_profiles, many=True).data

    def get_deleted_by(self, chat_message):
        all_profiles = chat_message.deleted_by.all()
        return DefaultProfileSerializer(all_profiles, many=True).data


    class Meta:
        model = ChatMessage
        fields = ['id', 'chat', 'profile', 'text', 'created_at', 'media', 'post', 'post_message', 'deleted_by', 'delivered_to']


class ChatListSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    profiles = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    blocked_by = DefaultProfileSerializer(read_only=True)
    
    def get_last_message(self, obj):
        if obj.last_message and not obj.last_message.is_deleted:
            return GetChatMessageSerializer(obj.last_message).data
        else:
            return dict()

    def get_profiles(self, obj):
        participants = Profile.objects.filter(chatparticipant_profile__chat=obj, is_deleted=False)
        return DefaultProfileSerializer(participants, many=True).data

    def get_unread_count(self, obj):
        try:
            profile = self.context.get('profile')
            chat_messages = list(ChatMessage.objects.filter(chat=obj, is_deleted=False, read_by=profile).values_list('id', flat=True))
            messages_count = ChatMessage.objects.filter(chat=obj, is_deleted=False).exclude(id__in=chat_messages).count()
            return messages_count
        except Exception as e:
            print(e)
            return 0

    class Meta:
        model = Chat
        fields = ['id', 'title', 'chat_type', 'created_by', 'created_at', 'last_message', 'profiles', 'unread_count' , 'blocked_by']


class GetChatSerializer(serializers.ModelSerializer):
    chat_messages = serializers.SerializerMethodField()
    profiles = serializers.SerializerMethodField()
    banner = serializers.SerializerMethodField()

    def get_chat_messages(self, obj):
        try:
            profile = self.context.get("profile")
            chat_messages = ChatMessage.objects.filter(chat=obj, is_deleted=False).exclude(deleted_by=profile).order_by('-created_at')
            return GetChatMessageSerializer(chat_messages, many=True).data
            
        except Exception as e:
            print(e)
            return 'No messages for this chat yet.'

    def get_banner(self, obj):
        if obj.banner:
            return f"{settings.S3_BUCKET_LINK}{obj.banner}"
        else:
            return None

    def get_profiles(self, obj):
        participants = list(ChatParticipant.objects.filter(chat=obj, chat__is_deleted=False, is_deleted=False).values_list('profile__id', flat=True))
        profiles = Profile.objects.filter(id__in=participants, is_deleted=False, user__is_active=True)
        return DefaultProfileSerializer(profiles, many=True).data
    
    # def get_profiles(self, obj):
    #     participants = ChatParticipant.objects.filter(chat=obj)
    #     for i in participants:
    #         if i.created_by != i.profile:
    #             profiles = Profile.objects.filter(id=i.profile.id, is_deleted=False, user__is_active=True)
    #             return DefaultProfileSerializer(profiles, many=True).data

    # def get_profiles(self, obj):
    #     try:
    #         participant = ChatParticipant.objects.filter(chat=obj, chat__is_deleted=False, is_deleted=False)
    #         for i in participant[:1]:
    #             profiles = Profile.objects.filter(id=i.id, is_deleted=False, user__is_active=True)
    #             return DefaultProfileSerializer(profiles, many=True).data
    #     except Exception as e:
    #         print('*********', e)
    #         return None
    class Meta:
        model = Chat
        fields = ['id', 'title', 'chat_type', 'created_at', 'chat_messages', 'profiles', 'banner']


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'

class ChatParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatParticipant
        fields = '__all__'

class GetChatSerializerSocket(serializers.ModelSerializer):
    profiles = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()

    def get_created_by(self , obj):
        return str(obj.created_by)

    def get_profiles(self, obj):
        participants = Profile.objects.filter(chatparticipant_profile__chat=obj, is_deleted=False)
        return DefaultProfileSerializer(participants, many=True).data

    class Meta:
        model = Chat
        fields = ['id', 'title', 'chat_type', 'created_at', 'profiles', 'created_by']
