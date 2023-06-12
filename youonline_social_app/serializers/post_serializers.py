import datetime
import profile
from rest_framework import serializers

from youonline_social_app.websockets.Constants import send_notifications_ws
from ..models import *
from community_app.models import *
from ..constants import password_validator
import random, string
from rest_framework import status
from .. import views
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
from moviepy.editor import VideoFileClip
import random, string
from . users_serializers import *
from community_app.serializers import *
from video_app.serializers import *
from . import users_serializers
from ..custom_api_settings import CustomPagination
from youonline_social_app.serialized_methods import *
from firebase_admin import _messaging_encoder
from firebase_admin.messaging import Notification as FB_Notification
Message = _messaging_encoder.Message


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name']


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']

class AllPostTestSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()


    def get_profile(self, post):
        return serialized_post_profile(post.profile)


    def get_media(self, post):
        if post.profile_picture_post:
            # return GetPostProfilePictureSerializer(post.post_profile_picture.all(), many=True).data
            return serialized_profile_picture(post.post_profile_picture.all()[0])
        elif post.cover_post:
            # return GetPostCoverPictureSerializer(post.post_cover.all(), many=True).data
            return serialized_cover_picture(post.post_cover.all()[0])
        elif post.normal_post:
            # return PostMediaSerializer(post.post_post.all(), many=True).data
            return serilaized_post_media(post.post_post.all())
        elif post.video_post and post.media_post or (post.page_post and not post.page_banner) or (post.group_post and not post.group_banner):
            if post.post_post.all().count() > 0:
                return serilaized_post_media(post.post_post.all())
                # return PostMediaSerializer(post.post_post.all(), many=True).data
            else:
                return serilaized_post_media(post.sub_post.all())
                # return PostMediaSerializer(post.sub_post.all(), many=True).data
        elif post.album_post:
            # return users_serializers.GetUserAlbumMediaSerializer(post.useralbummedia_post.all(), many=True).data
            return serialized_album_media(post.useralbummedia_post.all())
        elif post.video_module:
            try:
                profile = self.context.get("profile")
                return GetVideoSerializer(post.videomodule_post.all(), many=True, context={"profile": profile}).data
            except:
                return GetVideoSerializer(post.videomodule_post.all(), many=True).data
        elif post.group_banner:
            return GetPostGroupBannerSerializer(post.groupbanner_post.all(), many=True).data
        elif post.page_banner:
            return GetPostPageBannerSerializer(post.pagebanner_post.all(), many=True).data
        else:
            return serilaized_post_media(post.post_post.all())
            # return PostMediaSerializer(post.post_post.all(), many=True).data

    class Meta:
        model = Post
        fields = '__all__'

class GetCompanySerializer(serializers.ModelSerializer):
    cover_image = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()

    
    def get_country(self, obj):
        return CountrySerializer(obj.country).data

    def get_state(self, obj):
        return StateSerializer(obj.state).data

    def get_city(self, obj):
        return CitySerializer(obj.city).data

    def get_logo(self, obj):
        try:
            logo = CompanyLogo.objects.get(company=obj, is_deleted=False)
            return f"{settings.S3_BUCKET_LINK}{logo.logo}"
        except:
            return None

    def get_cover_image(self, obj):
        try:
            cover_image = CompanyCoverImage.objects.get(company=obj, is_deleted=False)
            return f"{settings.S3_BUCKET_LINK}{cover_image.cover_image}"
        except:
            return None
    class Meta:
        model = Company
        fields = [
                'id', 'profile', 'name', 'about', 'company_type', 'company_status',
                'license_number', 'email', 'phone', 'dial_code', 'country', 'state', 'city', 
                'street_address', 'longitude','latitude', 'logo', 'cover_image'
                ] 

class DefaultProfileSerializer(serializers.ModelSerializer):
    """
    This is the default Profile Serializer used to get the basic UserInformation.
    """
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()
    cover_picture = serializers.SerializerMethodField()
    mobile_number = serializers.SerializerMethodField()

    def get_mobile_number(self, obj):
        # if obj.user.mobile_number:
        #     return obj.user.mobile_number
        # else:
        #     return None
        try:
            return User.objects.get(profile_user=obj).mobile_number
        except:
            return None


    def get_first_name(self, obj):
        return User.objects.get(profile_user=obj).first_name

    def get_email(self, obj):
        return User.objects.get(profile_user=obj).email

    def get_username(self, obj):
        return User.objects.get(profile_user=obj).username

    def get_last_name(self, obj):
        return User.objects.get(profile_user=obj).last_name

    def get_is_admin(self, obj):
        is_admin = False
        user = User.objects.get(profile_user=obj)
        if user.is_admin == True:
            is_admin = True
            return is_admin
        else:
            return is_admin
        

    def get_profile_picture(self, obj):
        try:
            profile_picture = ProfilePicture.objects.get(profile=obj.id)
            return f"{settings.S3_BUCKET_LINK}{profile_picture.picture}"
        except:
            profile_picture = None
        return profile_picture
    
    def get_cover_picture(self, obj):
        try:
            cover_picture = CoverPicture.objects.get(profile=obj)
            return f"{settings.S3_BUCKET_LINK}{cover_picture.cover}"
        except Exception as e:
            print(e)
            cover_picture = None
        return cover_picture

    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'gender', 'is_admin', 
        'profile_picture', 'cover_picture', 'country', 'state', 'city', 'bio', 'mobile_number',
        'street_adress', 'longitude', 'latitude' ,'dial_code','mobile_privacy',
        'special_offer_privacy', 'recommended_privacy']


class ClassifiedProfileSerializer(serializers.ModelSerializer):
    """
    This is the default Profile Serializer used to get the basic UserInformation.
    """
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()
    cover_picture = serializers.SerializerMethodField()

    def get_first_name(self, obj):
        return User.objects.get(profile_user=obj).first_name

    def get_email(self, obj):
        return User.objects.get(profile_user=obj).email

    def get_username(self, obj):
        return User.objects.get(profile_user=obj).username

    def get_last_name(self, obj):
        return User.objects.get(profile_user=obj).last_name

    def get_is_admin(self, obj):
        is_admin = False
        user = User.objects.get(profile_user=obj)
        if user.is_admin == True:
            is_admin = True
            return is_admin
        else:
            return is_admin
        

    def get_profile_picture(self, obj):
        print(obj)
        try:
            profile_picture = ProfilePicture.objects.get(profile=obj.id)
            return f"{settings.S3_BUCKET_LINK}{profile_picture.picture}"
        except:
            profile_picture = None
        return profile_picture
    
    def get_cover_picture(self, obj):
        try:
            cover_picture = CoverPicture.objects.get(profile=obj)
            return f"{settings.S3_BUCKET_LINK}{cover_picture.cover}"
        except Exception as e:
            print(e)
            cover_picture = None
        return cover_picture

    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'gender', 'is_admin', 
        'profile_picture', 'cover_picture', 'country', 'state', 'city', 'bio', 
        'street_adress', 'longitude', 'latitude' ,'dial_code','mobile_privacy',
        'special_offer_privacy', 'recommended_privacy']


class PostProfileSerializer(serializers.ModelSerializer):

    def to_representation(self, profile):
        user = User.objects.get(profile_user=profile)
        try:
            profile_picture = UserProfilePicture.objects.get(profile=profile).picture.picture.url
            profile_picture = str(profile_picture.replace("/media/", settings.S3_BUCKET_LINK))
        except:
            profile_picture = None
        return_dict = {
            'id': profile.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'profile_picture': profile_picture
        }
        return return_dict
        

    class Meta:
        model = Profile
        fields = ['id']


class PostMediaSerializer(serializers.ModelSerializer):
    """
    PostMediaSerializer to serialize all the post objects.
    """
    class Meta:
        model = PostMedia
        fields = ('post_image', 'post_video', 'post_audio', 'post_gif', 'background_image')

    def to_representation(self, obj):
        return_dict = {}
        if obj.post_image:
            return_dict['post_image'] = f"{settings.S3_BUCKET_LINK}{obj.post_image}"
            return_dict['id'] = obj.post.id
            if obj.sub_post:
                return_dict['media_post_id'] = obj.sub_post.id
            else:
                return_dict['media_post_id'] = obj.post.id

        if obj.post_video:
            return_dict['post_video'] = f"{settings.S3_BUCKET_LINK}{obj.post_video}"
            if obj.vid_thumbnail:
                return_dict['video_thumbnail'] = f"{settings.S3_BUCKET_LINK}{obj.vid_thumbnail}"
            else:
                return_dict['video_thumbnail'] = ''
            return_dict['id'] = obj.post.id
            if obj.sub_post:
                return_dict['media_post_id'] = obj.sub_post.id
            else:
                return_dict['media_post_id'] = obj.post.id

        if obj.post_audio:
            return_dict['post_audio'] = f"{settings.S3_BUCKET_LINK}{obj.post_audio}"
            return_dict['id'] = obj.post.id
            if obj.sub_post:
                return_dict['media_post_id'] = obj.sub_post.id
            else:
                return_dict['media_post_id'] = obj.post.id

        if obj.post_gif:
            return_dict['post_gif'] = obj.post_gif
            return_dict['id'] = obj.post.id
            if obj.sub_post:
                return_dict['media_post_id'] = obj.sub_post.id
            else:
                return_dict['media_post_id'] = obj.post.id

        if obj.background_image:
            return_dict['background_image'] = f"{settings.S3_BUCKET_LINK}{obj.background_image}"
            return_dict['id'] = obj.post.id
            if obj.sub_post:
                return_dict['media_post_id'] = obj.sub_post.id
            else:
                return_dict['media_post_id'] = obj.post.id

        if obj.background_color:
            return_dict['background_color'] = obj.background_color
            return_dict['id'] = obj.post.id
            if obj.sub_post:
                return_dict['media_post_id'] = obj.sub_post.id
            else:
                return_dict['media_post_id'] = obj.post.id
        return return_dict


class PollOptionSerializer(serializers.ModelSerializer):
    """
    Serializer to get the Voters list and also check if the current user has voted for the given Option.
    """
    voters = serializers.SerializerMethodField()
    voted = serializers.SerializerMethodField()

    def get_voters(self, option):
        voters_list = list(PollVote.objects.filter(option=option).values_list('profile__id', flat=True))
        profiles = Profile.objects.filter(id__in=voters_list)
        return PostProfileSerializer(profiles, many=True).data

    def get_voted(self, option):
        profile = self.context.get("profile")
        try:
            vote = PollVote.objects.get(option=option, profile=profile)
            return True
        except:
            return False

    class Meta:
        model = PollOption
        fields = ['id', 'poll', 'option', 'total_votes', 'created_at', 'voters', 'voted']
        read_only_fields = fields


class PollSerializer(serializers.ModelSerializer):
    """
    Get the poll and all poll options
    """
    poll_options = serializers.SerializerMethodField()

    def get_poll_options(self, poll):
        profile = self.context.get("profile")
        options = PollOption.objects.filter(poll=poll)
        return PollOptionSerializer(options, many=True, context={"profile": profile}).data

    class Meta:
        model = Poll
        fields = ['id', 'description', 'poll_options', 'total_votes', 'expire_at', 'is_expired']
        read_only_fields = fields


class PostReactionSerializer(serializers.ModelSerializer):
    """
    Serializer used to create the PostReaction
    """

    class Meta:
        model = PostReaction
        fields = ('__all__')


class CommentMediaSerializer(serializers.ModelSerializer):
    """
    Serializer for comment Media such as images, videos, audio and gif
    """

    class Meta:
        model = CommentMedia
        fields = ('comment_image', 'comment_video', 'comment_audio', 'comment_gif')

    def to_representation(self, obj):
        return_dict = {}
        if obj.comment_image:
            return_dict['comment_image'] = f"{settings.S3_BUCKET_LINK}{obj.comment_image}"

        if obj.comment_video:
            return_dict['comment_video'] = f"{settings.S3_BUCKET_LINK}{obj.comment_video}"
        
        if obj.comment_audio:
            return_dict['comment_audio'] = f"{settings.S3_BUCKET_LINK}{obj.comment_audio}"
        
        if obj.comment_gif:
            return_dict['comment_gif'] = obj.comment_gif

        return return_dict
        

class PostCommentSerializer(serializers.ModelSerializer):
    comment_media = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    comment_reply = serializers.SerializerMethodField()
    reactions = serializers.SerializerMethodField()
    mentioned_profiles = serializers.SerializerMethodField()

    def get_mentioned_profiles(self, comnt):
        return UserTagSerializer(comnt.taguser_comment.all().order_by('-created_at'), many=True).data

    def get_comment_media(request, obj):
        return CommentMediaSerializer(obj.commentmedia_set.all().order_by('-created_at'), many=True).data

    def get_profile(request, obj):
        return DefaultProfileSerializer(obj.profile).data

    def get_comment_reply(request, obj):
        return GetCommentReplySerializer(obj.commentreply_set.all().order_by('-created_at'), many=True).data

    def get_reactions(request, obj):
        return CommentReactionSerializer(obj.commentreaction_set.all().order_by('-created_at'), many=True).data

    def get_mentioned_profiles(request, obj):
        mention_profile = TagUser.objects.filter(comment=obj)
        serializer = UserTagSerializer(mention_profile, many=True).data
        return serializer

    class Meta:
        model = PostComment
        fields = ('id', 'profile', 'post', 'text', 'created_at', 'updated_at', 'reactions_count',
                'replies_count', 'comment_media', 'comment_reply', 'reactions', 'mentioned_profiles')


class CommentReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReaction
        fields = ('__all__')


class CommentReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReply
        fields = ['id', 'comment', 'profile', 'text', 'reactions_count', 'created_at']


class GetCommentReplySerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    comment_media = serializers.SerializerMethodField()
    reactions = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()
    mentioned_profiles = serializers.SerializerMethodField()

    class Meta:
        model = CommentReply
        fields = ['id', 'comment', 'post', 'profile', 'text', 'reactions_count',
                 'created_at', 'comment_media', 'reactions', 'mentioned_profiles']
    
    def get_profile(request, obj):
        return DefaultProfileSerializer(obj.profile).data
    
    def get_post(request, obj):
        return obj.comment.post.id

    def get_comment_media(request, obj):
        return CommentReplyMediaSerializer(obj.commentreplymedia_set.all().order_by('-created_at'), many=True).data

    def get_reactions(request, obj):
        return CommentReplyReactionSerializer(obj.commentreplyreaction_set.all().order_by('-created_at'), many=True).data

    def get_mentioned_profiles(request, obj):
        mention_profile = TagUser.objects.filter(reply_comment=obj)
        serializer = UserTagSerializer(mention_profile, many=True).data
        return serializer

class CommentReplyMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReplyMedia
        fields = ('reply_image', 'reply_video', 'reply_audio', 'reply_gif')

    def to_representation(self, obj):
        return_dict = {}
        if obj.reply_image:
            return_dict['reply_image'] = f"{settings.S3_BUCKET_LINK}{obj.reply_image}"

        if obj.reply_video:
            return_dict['reply_video'] = f"{settings.S3_BUCKET_LINK}{obj.reply_video}"
        
        if obj.reply_audio:
            return_dict['reply_audio'] = f"{settings.S3_BUCKET_LINK}{obj.reply_audio}"
        
        if obj.reply_gif:
            return_dict['reply_gif'] = obj.reply_gif

        return return_dict


class CommentReplyReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReplyReaction
        fields = ('__all__')


class PostSerializer(serializers.ModelSerializer):
    """
    PostSerializer is used to create post here.
    """
    background_color = serializers.CharField(max_length=32, allow_null=True, required=False)
    group = serializers.CharField(max_length=64, allow_null=True, required=False)
    page = serializers.CharField(max_length=64, allow_null=True, required=False)
    poll_duration = serializers.CharField(max_length=32, allow_null=True, required=False)
    post_image = serializers.ListField(required=False, allow_null=True,
                                       child=serializers.FileField(
                                           max_length=1000000, allow_empty_file=True, use_url=False
                                       ))
    post_video = serializers.FileField(max_length=1000000, required=False, allow_empty_file=True, use_url=False)
    post_audio = serializers.ListField(required=False, allow_null=True,
                                       child=serializers.FileField(
                                           max_length=1000000, allow_empty_file=True, use_url=False
                                       ))
    post_gif = serializers.ListField(required=False, allow_null=True,
                                     child=serializers.CharField(max_length=255, allow_blank=True, trim_whitespace=False))
    background_image = serializers.FileField(max_length=1000000, required=False, allow_empty_file=True, use_url=False)
    poll_description = serializers.CharField(max_length=1000000, allow_null=True, required=False)
    poll_options = serializers.ListField(required=False, allow_null=True,
                                       child=serializers.CharField(
                                           max_length=1000000, allow_null=True, allow_blank=True
                                       ))
    tagged_profiles = serializers.ListField(required=False, allow_null=True,
                                       child=serializers.CharField(
                                           max_length=1000000, allow_null=True, allow_blank=True
                                       ))
    mentioned_profiles = serializers.ListField(required=False, allow_null=True,
                                       child=serializers.CharField(
                                           max_length=1000000, allow_null=True, allow_blank=True
                                       ))


    class Meta:
        model = Post
        fields = '__all__'

    def create(self, validated_data):
        """
        Override create method to create the Post with custom validations.

        # MAIN VALIDATIONS/FUNCTIONALITIES HANDLED IN THIS METHOD
        - Create post.
        - Check for page or group in request body and use that to create the post for page or group respectively.
        - Check if there is any media in the post
        - If there is only one media in the post then the post should be labeled as media post.
        - If there are multiple medias create separate sub posts for all those medias &&
            - Create One parent post as well to link all the sub posts with.
        - Tag friends logic also goes here if the user tags someone while creating the post.
        - Mentioned users logic also goes inside this method if user mentions someone while creating the post.
        """
        try:
            use = validated_data.pop('profile')
            try:
                user = Profile.objects.get(id=use.id)
            except ObjectDoesNotExist:
                error = serializers.ValidationError(
                    {
                        'success': False, 
                        'response': {
                            'message': 
                            'User does not exist'
                        }
                    }
                )
                error.status_code = 404
                raise error
        except:
            error = serializers.ValidationError(
                {
                    'success': False, 
                    'response': {
                        'message': 
                        'Please, Enter User ID'
                    }
                }
            )
            error.status_code = 400
            raise error

        try:
            text = validated_data.pop('text')
        except:
            text = None

        try:
            poll_description = validated_data.pop('poll_description')
        except:
            poll_description = None

        try:
            poll_options = validated_data.pop('poll_options')
        except:
            poll_options = None

        try:
            poll_duration = validated_data.pop('poll_duration')
        except:
            poll_duration = None

        try:
            feeling = validated_data.pop('feeling')
        except:
            feeling = None

        try:
            feeling_unicode = validated_data.pop('feeling_unicode')
        except:
            feeling_unicode = None

        try:
            activity = validated_data.pop('activity')
        except:
            activity = None

        try:
            activity_unicode = validated_data.pop('activity_unicode')
        except:
            activity_unicode = None

        # Location
        try:
            street_adress = validated_data.pop('street_adress')
        except:
            street_adress = None

        try:
            longitude = validated_data.pop('longitude')
        except:
            longitude = None

        try:
            latitude = validated_data.pop('latitude')
        except:
            latitude = None

        try:
            background_color = validated_data.pop('background_color')
        except:
            background_color = None

        try:
            privacy = validated_data.pop('privacy')
        except:
            privacy = 'Public'

        try:
            group = validated_data.pop('group')
            try:
                group_obj = Group.objects.get(id=group)
            except ObjectDoesNotExist:
                error = serializers.ValidationError(
                    {'success': False, 'response': {'message': 'Group does not exist'}})
                error.status_code = 404
                raise error
        except:
            group = None
            group_obj = None
        try:
            page = validated_data.pop('page')
            try:
                page_obj = Page.objects.get(id=page)
            except ObjectDoesNotExist:
                error = serializers.ValidationError(
                    {'success': False, 'response': {'message': 'Page does not exist'}})
                error.status_code = 404
                raise error
        except:
            page = None
            page_obj = None

        # create Post with the basic details
        post = Post.objects.create(
            profile=user,
            feeling=feeling,
            feeling_unicode=feeling_unicode,
            activity=activity,
            activity_unicode=activity_unicode,
            text=text,
            privacy=privacy,
            normal_post=True,
            group=group_obj,
            page=page_obj,
            street_adress=street_adress,
            longitude=longitude,
            latitude=latitude,
        )
        notifiers = NotifiersList.objects.create(post=post)
        notifiers.notifiers_list.add(user)
        notifiers.save()
        # Check if the post should to group
        if group_obj:
            post.group_post = True
            post.normal_post = False
            group_admins = list(GroupMember.objects.filter(group=group_obj,
                                is_admin=True).values_list('profile__id', flat=True))
            if group_obj.approval_required and user.id not in group_admins:
                post.is_approved = False
                post.is_deleted = True
            post.save()
        # Check if the post should to page
        if page_obj:
            post.page_post = True
            post.normal_post = False
            post.save()

        is_image_post = False
        is_video_post = False
        is_audio_post = False
        is_gif_post = False
        is_background_post = False
        is_color_post = False
        media_count = 0
        try:
            image = validated_data.pop('post_image')
            media_count += len(image)
        except:
            image = None
        try:
            audio = validated_data.pop('post_audio')
            media_count += len(audio)
        except:
            audio = None
        try:
            gif = validated_data.pop('post_gif')
            media_count += len(gif)
        except:
            gif = None
        try:
            video = validated_data['post_video']
            media_count += 1
        except:
            video = None
        # Check if there is atleast one image in the request body.
        if image is not None:
            image_medias = []
            image_posts = []
            for i in image:
                # Condition for 20MB Image Size
                if i.size > 20971520:
                    post.delete()
                    error = serializers.ValidationError({'success': False,
                                                         'response': {
                                                             'message': 'Error in post image size. Maximum allowed size is 20mb.'}})
                    error.status_code = 400
                    raise error
                # Check image format
                name = i.name.split('.')
                if name[-1].strip() in ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG']:
                    # Create PostMedia object for Images
                    image_media = PostMedia(
                        profile=user,
                        post=post,
                        post_image=i
                    )
                    image_media.save()
                    # Create Post for Media
                    image_post = Post(
                            profile=user,
                            text=text,
                            normal_post=False,
                            media_post=True,
                            privacy=post.privacy
                        )
                    image_posts.append(image_post)
                    image_medias.append(image_media)
                    is_image_post = True
                else:
                    post.delete()
                    raise serializers.ValidationError({'success': False,
                                                         'response': {
                                                             'message': 'Error in post_image field,'
                                                                        'Only these formats are allowed {}'.format(
                                                                 ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG'])}})
        if audio is not None:
            audio_medias = []
            audio_posts = []
            for i in audio:
                name = i.name.split('.')
                if name[-1] in ['mp3', 'MP3']:
                    audio_media = PostMedia(
                        profile=user,
                        post=post,
                        post_audio=i
                    )
                    audio_post = Post(
                            profile=user,
                            text=text,
                            normal_post=False,
                            media_post=True,
                            privacy=post.privacy
                        )
                    audio_posts.append(audio_post)
                    audio_medias.append(audio_media)
                    is_audio_post = True
                else:
                    post.delete()
                    raise serializers.ValidationError({'success': False,
                                                         'response': {
                                                             'message': 'Error in post_audio field,'
                                                                        'Only these formats are allowed {}'.format(
                                                                 ['mp3', 'MP3'])}})
        if gif is not None:
            for i in gif:
                gif_media = PostMedia(
                    profile=user,
                    post=post,
                    post_gif=i
                )
                gif_post = Post(
                        profile=user,
                        text=text,
                        normal_post=False,
                        media_post=True,
                        privacy=post.privacy
                    )
                is_gif_post = True
        if not background_color:
            try:
                background_image = validated_data['background_image']
            except:
                background_image = None
            if background_image is not None:
                if background_image.size > 20971520:
                    post.delete()
                    error = serializers.ValidationError({'success': False,
                                                         'response': {
                                                             'message': 'Error in background image size. Maximum allowed size is 20mb.'}})
                    error.status_code = 400
                    raise error
                name = background_image.name.split('.')
                if name[-1] in ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG']:
                    background_media = PostMedia(
                        profile=user,
                        post=post,
                        background_image=background_image
                    )
                    is_background_post = True
                else:
                    post.delete()
                    raise serializers.ValidationError({'success': False,
                                                         'response': {
                                                             'message': 'Error in background_image field,'
                                                                        'Only these formats are allowed {}'.format(
                                                                 ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG'])}})
        else:
            color_media = PostMedia(
                profile=user,
                post=post,
                background_color=background_color
            )
            is_color_post = True
        if poll_description:
            poll = Poll.objects.create(
                post=post,
                profile=user,
                description=poll_description
            )
            poll.duration = poll_duration
            current_time = datetime.datetime.now()
            if poll_duration == '24Hours':
                expiry_date = current_time + datetime.timedelta(days=1)
            elif poll_duration == '3Days':
                expiry_date = current_time + datetime.timedelta(days=3)
            elif poll_duration == '1Week':
                expiry_date = current_time + datetime.timedelta(days=7)
            elif poll_duration == '2Weeks':
                expiry_date = current_time + datetime.timedelta(days=14)
            else:
                expiry_date = current_time + datetime.timedelta(days=1)
            poll.expire_at = expiry_date
            poll.save()
            post.poll_post = True
            post.save()
            if poll_options is not None:
                for i in poll_options:
                    PollOption.objects.create(
                        poll=poll,
                        option=i,
                    )
            else:
                post.delete()
                raise serializers.ValidationError({'success': False, 'response':{'message': 'Poll Options not added.'}})

        # Tag Friends
        try:
            tagged_profiles = validated_data.pop('tagged_profiles')
            
            if tagged_profiles is not None:
                for i in tagged_profiles:
                    try:
                        tag_profile = Profile.objects.get(id=str(i))
                        TagUser.objects.create(
                            post=post,
                            tagged_profile=tag_profile,
                            tagged_by=post.profile
                        )
                        notifiers.notifiers_list.add(tag_profile)
                    except:
                        pass
                notifiers.save()
                notification = Notification(
                        type = 'TaggedPost',
                        profile = post.profile,
                        text = 'Tagged you in a post.',
                        post = post,
                    )
                notification.save()
                for i in tagged_profiles:
                    notification.notifiers_list.add(i)
                    try:
                        devices = FCMDevice.objects.filter(device_id=i.id)
                        fb_body = {
                            'comment_reply': 'null',
                            'created_at': str(datetime.datetime.now()),
                            'post_comment': 'null',
                            'type': 'TaggedPost',
                            'profile': str(i.id),
                            'post_profile': str(post.profile.id),
                            'text': f"{post.profile.user.first_name} {post.profile.user.last_name} tagged you in a post.",
                            'post': str(post.id),
                        }
                        devices.send_message(
                            Message(
                                data=fb_body,
                                notification=FB_Notification(
                                    title="Tagged Post",
                                    body=fb_body['text'],
                                    image=notification_image)
                        ))
                    except:
                        pass
                notification.save()
                try:
                    send_notifications_ws(notification)
                except:
                    pass
                try:
                    notification_image = UserProfilePicture.objects.get(profile=profile).picture.picture
                except Exception as e:
                    notification_image = None
        except:
            pass
        # Mentioned Friends
        try:
            mentioned_profiles = validated_data.pop('mentioned_profiles')
            
            if mentioned_profiles is not None:
                for i in mentioned_profiles:
                    print(i)
                    try:
                        mnd_profile = Profile.objects.get(id=str(i))
                        TagUser.objects.create(
                            post=post,
                            tagged_profile=mnd_profile,
                            tagged_by=post.profile,
                            is_mentioned=True
                        )
                        notifiers.notifiers_list.add(mnd_profile)
                    except:
                        pass
                notifiers.save()
                notification = Notification(
                        type = 'MentionedPost',
                        profile = post.profile,
                        text = 'Mentioned you in a post.',
                        post = post,
                    )
                notification.save()
                for i in mentioned_profiles:
                    notification.notifiers_list.add(i)
                    try:
                        devices = FCMDevice.objects.filter(device_id=i.id)
                        fb_body = {
                            'comment_reply': 'null',
                            'created_at': str(datetime.datetime.now()),
                            'post_comment': 'null',
                            'type': 'TaggedPost',
                            'profile': str(i.id),
                            'post_profile': str(post.profile.id),
                            'text': f"{post.profile.user.first_name} {post.profile.user.last_name} Mentioned you in a post.",
                            'post': str(post.id),
                        }
                        devices.send_message(
                            Message(
                                data=fb_body,
                                notification=FB_Notification(
                                    title="Mentioned Post",
                                    body=fb_body['text'],
                                    image=notification_image)
                        ))
                    except:
                        pass
                notification.save()
                try:
                    send_notifications_ws(notification)
                except:
                    pass
                try:
                    notification_image = UserProfilePicture.objects.get(profile=profile).picture.picture
                except Exception as e:
                    notification_image = None
        except Exception as err:
            print(err)
            pass
        if video is not None:
            name = video.name.split('.')
            if name[-1] in ['mp4', 'mkv', 'webm', 'avi', 'flv', 'wmv', 'mov', 'MP4', 'MKV', 'WEBM', 'AVI', 'FLV', 'WMV', 'MOV']:
                if video.size > 75000000:
                    post.delete()
                    error = serializers.ValidationError({'success': False,
                                                         'response': {
                                                             'message': 'Error in post video size. Maximum allowed size is 75mb.'}})
                    error.status_code = 400
                    raise error
                else:
                    obj = PostMedia(
                        profile=user,
                        post=post,
                        post_video=video
                    )
                    obj.save()
                    if media_count > 1:
                        video_post = Post(
                                profile=user,
                                text=text,
                                normal_post=False,
                                media_post=True,
                                video_post=True,
                                privacy=post.privacy
                            )
                        if group_obj:
                            video_post.group_post = True
                        if page_obj:
                            video_post.page_post = True
                        video_post.save()
                        obj.sub_post = video_post
                        obj.save()
                        MediaPostObject.objects.create(
                                parent_post=post,
                                child_post=video_post,
                            )
                    else:
                        post.video_post = True
                        post.media_post = True
                        post.save()
            else:
                post.delete()
                raise serializers.ValidationError({'success': False,
                                                     'response': {
                                                         'message': 'Error in post_video field,'
                                                                    'Only these formats are allowed {}'.format(
                                                             ['mp4', 'mkv', 'webm', 'avi', 'flv', 'wmv', 'mov', 'MP4', 'MKV', 'WEBM', 'AVI', 'FLV', 'WMV', 'MOV'])}})
        if is_image_post:
            for i in range(len(image_medias)):
                image_medias[i].save()
                if media_count > 1:
                    if group_obj:
                        image_posts[i].group_post = True
                    if page_obj:
                        image_posts[i].page_post = True
                    image_posts[i].save()
                    image_medias[i].sub_post = image_posts[i]
                    image_medias[i].save()
                    MediaPostObject.objects.create(
                            parent_post=post,
                            child_post=image_posts[i],
                        )
                else:
                    post.media_post = True
                    post.save()
        if is_audio_post:
            for i in range(len(audio_medias)):
                audio_medias[i].save()
                if media_count > 1:
                    if group_obj:
                        audio_posts[i].group_post = True
                    if page_obj:
                        audio_posts[i].page_post = True
                    audio_posts[i].save()
                    audio_medias[i].sub_post = audio_posts[i]
                    audio_medias[i].save()
                    MediaPostObject.objects.create(
                            parent_post=post,
                            child_post=audio_posts[i],
                        )
                else:
                    post.media_post = True
                    post.save()
        if is_gif_post:
            gif_media.save()
            if media_count > 1:
                if group_obj:
                    gif_post.group_post = True
                if page_obj:
                    gif_post.page_post = True
                gif_post.save()
                gif_media.sub_post = gif_post
                gif_media.save()
                MediaPostObject.objects.create(
                        parent_post=post,
                        child_post=gif_post,
                    )
            else:
                post.media_post = True
                post.save()
        if is_background_post:
            background_media.save()
        if is_color_post:
            color_media.save()
        return post


class CreateSharedPostSerializer(serializers.ModelSerializer):
    """
    - This serializer is used to create another post when user shares an existing post.
    - All the validations checks and tag friends logic also goes inside this serializer.
    """
    tagged_profiles = serializers.ListField(required=False, allow_null=True,
                                       child=serializers.CharField(
                                           max_length=1000000, allow_null=True, allow_blank=True
                                       ))

    class Meta:
        model = Post
        fields = '__all__'

    def create(self, validated_data):
        try:
            use = validated_data.pop('profile')
            try:
                user = Profile.objects.get(id=use.id)
            except ObjectDoesNotExist:
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
            feeling = validated_data.pop('feeling')
        except:
            feeling = None
        try:
            feeling_unicode = validated_data.pop('feeling_unicode')
        except:
            feeling_unicode = None
        try:
            activity = validated_data.pop('activity')
        except:
            activity = None
        try:
            activity_unicode = validated_data.pop('activity_unicode')
        except:
            activity_unicode = None
        # Location
        try:
            street_adress = validated_data.pop('street_adress')
        except:
            street_adress = None
        try:
            longitude = validated_data.pop('longitude')
        except:
            longitude = None
        try:
            latitude = validated_data.pop('latitude')
        except:
            latitude = None
        try:
            privacy = validated_data.pop('privacy')
        except:
            privacy = 'Public'
        post = Post.objects.create(
            profile=user,
            feeling=feeling,
            feeling_unicode=feeling_unicode,
            activity=activity,
            activity_unicode=activity_unicode,
            text=text,
            privacy=privacy,
            normal_post=True,
            street_adress=street_adress,
            longitude=longitude,
            latitude=latitude,
        )
        notifiers = NotifiersList.objects.create(post=post)
        notifiers.notifiers_list.add(user)
        notifiers.save()
        # Tag Friends
        try:
            tagged_profiles = validated_data.pop('tagged_profiles')
            if tagged_profiles is not None:
                for i in tagged_profiles:
                    try:
                        tag_profile = Profile.objects.get(id=str(i))
                        TagUser.objects.create(
                            post=post,
                            tagged_profile=tag_profile,
                            tagged_by=post.profile
                        )
                        notifiers.notifiers_list.add(tag_profile)
                    except:
                        pass
                notifiers.save()
                notification = Notification(
                        type = 'TaggedPost',
                        profile = post.profile,
                        text = 'Tagged you in a post.',
                        post = post,
                    )
                notification.save()
                for i in tagged_profiles:
                    notification.notifiers_list.add(i)
                    try:
                        devices = FCMDevice.objects.filter(device_id=i.id)
                        fb_body = {
                            'comment_reply': 'null',
                            'created_at': str(datetime.datetime.now()),
                            'post_comment': 'null',
                            'type': 'TaggedPost',
                            'profile': str(i.id),
                            'post_profile': str(post.profile.id),
                            'text': f"{post.profile.user.first_name} {post.profile.user.last_name} tagged you in a post.",
                            'post': str(post.id),
                        }
                        devices.send_message(
                            Message(
                                data=fb_body,
                                notification=FB_Notification(
                                    title="Tagged Post",
                                    body=fb_body['text'],
                                    image=notification_image)
                        ))
                    except:
                        pass
                notification.save()
                try:
                    send_notifications_ws(notification)
                except:
                    pass
                try:
                    notification_image = UserProfilePicture.objects.get(profile=profile).picture.picture
                except Exception as e:
                    notification_image = None
        except:
            pass
        return post


class PostUpdateSerializer(serializers.ModelSerializer):
    """
    This serializer is used only to update the post text.
    """
    class Meta:
        model = Post
        fields = '__all__'


class GetPostProfilePictureSerializer(serializers.ModelSerializer):
    """
    Serializer to only get the id and profile picture link.
    """

    class Meta:
        model = ProfilePicture
        fields = ['picture', 'id']

    def to_representation(self, obj):
        return_dict = {}
        if obj.picture:
            return_dict["picture"] = f"{settings.S3_BUCKET_LINK}{obj.picture}"
        else:
            return_dict["picture"] = None
        return_dict["id"] = obj.post.id
        return return_dict


class GetPostCoverPictureSerializer(serializers.ModelSerializer):
    """
    Serializer to get the Cover picture of the user with the post.
    """
    picture = serializers.SerializerMethodField()
    class Meta:
        model = CoverPicture
        fields = ['picture', 'id']

    def to_representation(self, obj):
        return_dict = {}
        if obj.cover:
            return_dict["picture"] = f"{settings.S3_BUCKET_LINK}{obj.cover}"
        else:
            return_dict["picture"] = None
        return_dict["id"] = obj.post.id
        return return_dict


class GetUserFullNameSerializer(serializers.ModelSerializer):
    # Serializer to concat the first name and last name of the user
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class PostGetSerializer(serializers.ModelSerializer):
    """
    This serializer is used to serializer all the data for the post.
    - Some methods are coming from serialized_methods.py.
        - That was done to improve the performance of the API response.
    """
    profile = serializers.SerializerMethodField()
    group = DefaultGroupSerializer()
    page = GetPageSerializer()
    friend = serializers.SerializerMethodField()
    feeling = serializers.SerializerMethodField()
    activity = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()
    poll = serializers.SerializerMethodField()
    reactions = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    saved_post = serializers.SerializerMethodField()
    notifications_on = serializers.SerializerMethodField()
    post_album = serializers.SerializerMethodField()
    shared_post = serializers.SerializerMethodField()
 

    def get_post_album(self, post):
        if post.album_post:
            try:
                album_post = AlbumPost.objects.get(post=post)
                return users_serializers.GetAlbumPostSerializer(album_post).data
            except Exception as e:
                return None
        else:
            return None

    def get_feeling(self, post):
        return_dict = {
            "feeling": post.feeling,
            "feeling_unicode": post.feeling_unicode,
        }
        return return_dict

    def get_activity(self, post):
        return_dict = {
            "activity": post.activity,
            "activity_unicode": post.activity_unicode,
        }
        return return_dict

    def get_profile(self, post):
        return serialized_post_profile(post.profile)

    def get_media(self, post):
        if post.profile_picture_post:
            # return GetPostProfilePictureSerializer(post.post_profile_picture.all(), many=True).data
            return serialized_profile_picture(post.post_profile_picture.all()[0])
        elif post.cover_post:
            # return GetPostCoverPictureSerializer(post.post_cover.all(), many=True).data
            return serialized_cover_picture(post.post_cover.all()[0])
        elif post.normal_post:
            # return PostMediaSerializer(post.post_post.all(), many=True).data
            return serilaized_post_media(post.post_post.filter(is_deleted=False))
        elif post.video_post and post.media_post or (post.page_post and not post.page_banner and not post.page_logo) or (post.group_post and not post.group_banner and not post.group_logo):
            if post.post_post.all().count() > 0:
                return serilaized_post_media(post.post_post.all())
                # return PostMediaSerializer(post.post_post.all(), many=True).data
            else:
                return serilaized_post_media(post.sub_post.all())
                # return PostMediaSerializer(post.sub_post.all(), many=True).data
        elif post.album_post:
            # return users_serializers.GetUserAlbumMediaSerializer(post.useralbummedia_post.all(), many=True).data
            return serialized_album_media(post.useralbummedia_post.all())
        elif post.video_module:
            try:
                profile = self.context.get("profile")
                return GetVideoSerializer(post.videomodule_post.all(), many=True, context={"profile": profile}).data
            except:
                return GetVideoSerializer(post.videomodule_post.all(), many=True).data
        elif post.group_banner:
            return GetPostGroupBannerSerializer(post.groupbanner_post.all(), many=True).data
        elif post.page_banner:
            return GetPostPageBannerSerializer(post.pagebanner_post.all(), many=True).data
        elif post.group_logo:
            return GetPostGroupLogoSerializer(post.grouplogo_post.all(), many=True).data
        elif post.page_logo:
            return GetPostPageLogoSerializer(post.pagelogo_post.all(), many=True).data
        else:
            return serilaized_post_media(post.post_post.all())
            # return PostMediaSerializer(post.post_post.all(), many=True).data

    def get_reactions(self, post):
        return serialized_post_reactions(post.postreaction_post.all()[:2])


    def get_poll(self, post):
        if post.poll_post:
            # return PollSerializer(post.pollpost_post.all()[0], context={"profile": self.context.get("profile")}).data
            return serialized_post_poll(post.pollpost_post.all()[0])
        else:
            return None

    def get_tags(self, post):
        tags = []
        for i in post.taguser_post.all():
            return_dict = {
                "id": i.id,
                "tagged_profile": serialized_post_profile(i.tagged_profile),
                "tagged_by": serialized_post_profile(i.tagged_by),
                "post": i.post.id,
                "created_at": i.created_at,
                "is_mentioned" : i.is_mentioned
            }
            tags.append(return_dict)
        return tags
        
    def get_saved_post(self, post):
        try:
            profile = self.context.get("profile")
            try:
                s_post = SavedPost.objects.get(profile=profile, post=post)
                saved_post = True
            except:
                saved_post = False
        except:
            saved_post = False
        return saved_post

    def get_notifications_on(self, post):
        try:
            profile = self.context.get("profile")
        except:
            return None
        try:
            notifiers = NotifiersList.objects.get(post=post)
            if profile in notifiers.notifiers_list.all():
                notifications_on = True
            else:
                notifications_on = False
        except Exception as e:
            notifications_on = False
        return notifications_on

    def get_shared_post(self, post):
        if post.shared_post:
            return PostGetSerializer(post.sharedpost_post.all()[0].shared_post).data
        else:
            return None

    def get_friend(self, post):
        if post.shared_post:
            return DefaultProfileSerializer(post.sharedpost_post.all()[0].friend).data
        else:
            return None

    class Meta:
        model = Post
        fields = ['id', 'profile', 'feeling', 'activity', 'text', 'created_at',
                  'privacy', 'reactions', 'reactions_count', 'comments_count', 'is_hidden',
                  'media', 'poll', 'video_module', 'media_post', 'video_post',
                  'profile_picture_post', 'cover_post', 'normal_post', 'album_post',
                  'group_post', 'group', 'group_banner', 'group_logo', 'page_post', 'page',
                  'page_banner', 'page_logo', 'street_adress', 'longitude', 'latitude', 'tags', 'saved_post',
                  'notifications_on', 'shared_post', 'friend', 'post_album', 'is_approved', 'is_declined', ]
        read_only_fields = fields


class UserTagSerializer(serializers.ModelSerializer):
    """
    Serializer to get the details of Tagged Users.
    """
    tagged_profile = serializers.SerializerMethodField()
    tagged_by = serializers.SerializerMethodField()
    
    class Meta:
        model = TagUser
        fields = ['id', 'tagged_profile', 'tagged_by', 'post', 'comment', 'created_at', 'is_mentioned']

    def get_tagged_profile(self, obj):
        return serialized_post_profile(obj.tagged_profile)

    def get_tagged_by(self, obj):
        return serialized_post_profile(obj.tagged_by)


class UserReactionSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    def get_profile(self, profile):
        return GetUserFullNameSerializer(profile.user).data

    def get_profile_picture(self, profile):
        try:
            profile_picture = ProfilePicture.objects.get(profile=profile).profile_picture.url
            profile_picture = str(profile_picture.replace("/media/", settings.S3_BUCKET_LINK))
        except:
            profile_picture = None
        return profile_picture

    class Meta:
        model = Profile
        fields = ['id', 'profile', 'profile_picture']


class GetUserReactionSerializer(serializers.ModelSerializer):

    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    def get_first_name(self, obj):
        return User.objects.get(profile_user=obj).first_name

    def get_username(self, obj):
        return User.objects.get(profile_user=obj).username

    def get_last_name(self, obj):
        return User.objects.get(profile_user=obj).last_name

    def get_profile_picture(self, obj):
        try:
            profile_picture = UserProfilePicture.objects.get(profile=obj).picture.picture.url
            profile_picture = str(profile_picture.replace("/media/", settings.S3_BUCKET_LINK))
        except:
            profile_picture = None
        return profile_picture

    

    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name', 'username', 'profile_picture']



class GetPostReactionSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    reactions = serializers.SerializerMethodField()


    class Meta:
        model = PostReaction
        fields = ['post', 'profile', 'type', 'reactions']
    
    def get_profile(self, obj):
        user = self.context.get('user')
        try:
            profile = Profile.objects.get(user=user, is_deleted=False, user__is_active=True)
            serializer = GetUserReactionSerializer(profile).data
            return serializer
        except Exception as e:
            pass
    
    def get_reactions(self, obj):
        post = self.context.get('post')
        like = PostReaction.objects.filter(post=post, type='like').count()
        love = PostReaction.objects.filter(post=post, type='love').count()
        haha = PostReaction.objects.filter(post=post, type='haha').count()
        wow = PostReaction.objects.filter(post=post, type='wow').count()
        sad = PostReaction.objects.filter(post=post, type='sad').count()
        angry = PostReaction.objects.filter(post=post, type='angry').count()
        reactions = dict()
        reactions['like'] = like
        reactions['love'] = love
        reactions['haha'] = haha
        reactions['wow'] = wow
        reactions['sad'] = sad
        reactions['angry'] = angry
        return reactions
        
        


class PostCommentReactionSerializer(serializers.ModelSerializer):
    # Serializer to create post comment reaction
    class Meta:
        model = CommentReaction
        fields = ['id', 'comment', 'profile', 'type', 'react_unicode']


class SavedPostSerializer(serializers.ModelSerializer):
    # Serializer to create Saved Post object.
    class Meta:
        model = SavedPost
        fields = '__all__'


class HiddenPostSerializer(serializers.ModelSerializer):
    """
    Serializer to create hidden post object
    """
    class Meta:
        model = HiddenPost
        fields = '__all__'


class PostDislikeSerializer(serializers.ModelSerializer):
    """
    Serializer to create post dislike object.
        - This was done for video module posts
    """
    class Meta:
        model = PostDislike
        fields = '__all__'


class GetPostDislikeSerializer(serializers.ModelSerializer):
    """
    Get the dislike object for a post.
    """
    class Meta:
        model = PostDislike
        fields = '__all__'


class TotalPostReactionSerializer(serializers.ModelSerializer):
    profile = GetUserReactionSerializer()
    class Meta:
        model = PostReaction
        fields = ['id', 'post', 'profile', 'type', 'react_unicode', 'created_at', 'updated_at', 'is_deleted'] 

      
class ReportPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportPost
        fields = '__all__'


class GetReportPostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportPostCategory
        fields = '__all__'

class GetPackagePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackagePlan
        fields = '__all__'
        
class UserProfilePictureSerializer(serializers.ModelSerializer):
    picture = serializers.SerializerMethodField()

    def get_picture(self, obj):
        if obj.picture:
            return f"{settings.S3_BUCKET_LINK}{obj.picture}"
        else:
            return None
    class Meta:
        model = ProfilePicture
        fields = ['id', 'picture'] 
        
class UserCoverPictureSerializer(serializers.ModelSerializer):
    cover = serializers.SerializerMethodField()

    def get_cover(self, obj):
        if obj.cover:
            return f"{settings.S3_BUCKET_LINK}{obj.cover}"
        else:
            return None
    class Meta:
        model = CoverPicture
        fields = ['id', 'cover'] 



class SearchUserProfileSerializer(serializers.ModelSerializer):
    """
    This is the default Profile Serializer used to get the basic UserInformation.
    """
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()
    cover_picture = serializers.SerializerMethodField()
    mobile_number = serializers.SerializerMethodField()
    # business_profile = serializers.SerializerMethodField()
    total_profile_views = serializers.SerializerMethodField()
    total_ads_view = serializers.SerializerMethodField()
    total_active_ads = serializers.SerializerMethodField()

    def get_mobile_number(self, obj):
        if obj.user.mobile_number:
            return obj.user.mobile_number
        else:
            return None
    # def get_business_profile(self, obj):
    #     try:
    #         company = Company.objects.get(profile=obj, is_deleted=False)
    #         return GetCompanySerializer(company).data

    #     except Exception as e:
    #         print('**********', e)
    
    def get_total_profile_views(self, obj):
        return ProfileView.objects.filter(profile=obj).count()
    
    def get_total_ads_view(self, obj):

        visited_profile = self.context.get('visited_profile')
        classified_counts = list(Classified.objects.filter(profile=visited_profile, is_deleted=False, is_active=True).values_list('view_count', flat=True))
        automotive_count = list(Automotive.objects.filter(profile=visited_profile, is_deleted=False, is_active=True).values_list('view_count', flat=True))
        property_object_count = list(Property.objects.filter(profile=visited_profile, is_deleted=False, is_active=True).values_list('view_count', flat=True))
        job_count = list(Job.objects.filter(profile=visited_profile, is_deleted=False, is_active=True).values_list('view_count', flat=True))

        classified_counts = sum(classified_counts)
        automotive_count = sum(automotive_count)
        property_object_count = sum(property_object_count)
        job_count = sum(job_count)

        total_ads = classified_counts + automotive_count + property_object_count + job_count
        return total_ads

    def get_total_active_ads(self, obj):
        classified = Classified.objects.filter(is_active=True, is_deleted=False).count()
        automotive = Automotive.objects.filter(is_active=True, is_deleted=False).count()
        property_object = Property.objects.filter(is_active=True, is_deleted=False).count()
        job = Job.objects.filter(is_active=True, is_deleted=False).count()
        total_ads = classified + automotive + property_object + job
        return total_ads

    def get_first_name(self, obj):
        return User.objects.get(profile_user=obj).first_name

    def get_email(self, obj):
        return User.objects.get(profile_user=obj).email

    def get_username(self, obj):
        return User.objects.get(profile_user=obj).username

    def get_last_name(self, obj):
        return User.objects.get(profile_user=obj).last_name

    def get_is_admin(self, obj):
        is_admin = False
        user = User.objects.get(profile_user=obj)
        if user.is_admin == True:
            is_admin = True
            return is_admin
        else:
            return is_admin
        

    def get_profile_picture(self, obj):
        print(obj)
        try:
            profile_picture = ProfilePicture.objects.get(profile=obj.id)
            return f"{settings.S3_BUCKET_LINK}{profile_picture.picture}"
        except:
            profile_picture = None
        return profile_picture
    
    def get_cover_picture(self, obj):
        try:
            cover_picture = CoverPicture.objects.get(profile=obj)
            return f"{settings.S3_BUCKET_LINK}{cover_picture.cover}"
        except Exception as e:
            print(e)
            cover_picture = None
        return cover_picture

    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'gender', 'is_admin', 
        'profile_picture', 'cover_picture', 'country', 'state', 'city', 'bio', 
        'street_adress', 'longitude', 'latitude' ,'dial_code','mobile_privacy', 'mobile_number',
        'special_offer_privacy', 'recommended_privacy', 'total_profile_views', 'total_active_ads', 'total_ads_view']


class DealDataSerializer(serializers.ModelSerializer):
    # start_date = serializers.SerializerMethodField()
    # end_date = serializers.SerializerMethodField()

    # def get_start_date(self, obj):
    #     if obj.start_date:
    #         my_date = obj.start_date.strftime("%Y-%m-%d %H:%M")

    # def get_end_date(self, obj):
    #     if obj.end_date:
    #         my_date = obj.end_date.strftime("%Y-%m-%d %H:%M")
    
    class Meta:
        model = DealData
        fields = [
                'id',
                'automotive',
                'property',
                'classified',
                'discount_percentage',
                'discounted_price',
                'start_date',
                'end_date',
                'deal_automotive',
                'deal_property',
                'deal_classified',
                'is_expired',
                'is_deleted',
                'created_at',
                'updated_at'
            ]