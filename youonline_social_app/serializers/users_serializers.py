
import datetime
from tokenize import Token
from job_app.models import Company, CompanyCoverImage, CompanyLogo
from rest_framework import serializers
from ..models import *
from ..constants import *
from rest_framework import status
from .. import views
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
from django.db.models import Q
from moviepy.editor import VideoFileClip
from . post_serializers import *
from fcm_django.models import FCMDevice
from youonline_social_app.serialized_methods import *


class GetUserProfileSerializer(serializers.ModelSerializer):
    """
    This serializer is used to get all the profile info for a given profile
    """
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()
    cover_picture = serializers.SerializerMethodField()
    first_login = serializers.SerializerMethodField()
    social_account = serializers.SerializerMethodField()
    social_platform = serializers.SerializerMethodField()

    def get_first_name(self, obj):
        return User.objects.get(profile_user=obj).first_name

    def get_last_name(self, obj):
        return User.objects.get(profile_user=obj).last_name

    def get_username(self, obj):
        return User.objects.get(profile_user=obj).username

    def get_email(self, obj):
        return User.objects.get(profile_user=obj).email

    def get_first_login(self, obj):
        history = LoginHistory.objects.filter(profile=obj)
        if history.count() > 0:
            return False
        else:
            return True

    def get_social_account(self, obj):
        if obj:
            user = Profile.objects.get(user=obj.user).user
            if user.social_account:
                return True
            else:
                return False

    def get_social_platform(self, obj):
        if obj:
            user = Profile.objects.get(user=obj.user).user
            if user.social_platform == 'Google':
                return 'Google'
            else:
                return 'Facebook'

    def get_profile_picture(self, obj):
        try:
            profile_picture = UserProfilePicture.objects.get(profile=obj).picture.picture.url
            profile_picture = str(profile_picture.replace("/media/", settings.S3_BUCKET_LINK))
        except:
            profile_picture = None
        return profile_picture

    def get_cover_picture(self, obj):
        try:
            cover_picture = UserCoverPicture.objects.get(profile=obj).cover.cover.url
            cover_picture = str(cover_picture.replace("/media/", settings.S3_BUCKET_LINK))
        except Exception as e:
            cover_picture = None
        return cover_picture

    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name', 'profile_picture', 'cover_picture',
                  'username', 'email', 'birth_date', 'bio', 'first_login', 'social_account', 'social_platform']


# class SearchUserProfileSerializer(serializers.ModelSerializer):
#     """
#     This serializer is used to get the response after a search result.
#     """
#     first_name = serializers.SerializerMethodField()
#     last_name = serializers.SerializerMethodField()
#     email = serializers.SerializerMethodField()
#     username = serializers.SerializerMethodField()
#     is_admin = serializers.SerializerMethodField()
#     # maiden_name = serializers.SerializerMethodField()
#     mobile_number = serializers.SerializerMethodField()
#     profile_picture = serializers.SerializerMethodField()
    # cover_picture = serializers.SerializerMethodField()
    # request_sent = serializers.SerializerMethodField()
    # request_received = serializers.SerializerMethodField()
    # is_friend = serializers.SerializerMethodField()
    # has_followed = serializers.SerializerMethodField()
    # followed_by = serializers.SerializerMethodField()
    # own_profile = serializers.SerializerMethodField()
    # request_id = serializers.SerializerMethodField()
    # total_views = serializers.SerializerMethodField()
    # mutual_friends = serializers.SerializerMethodField()
    # total_posts = serializers.SerializerMethodField()
    # privacy_flags = serializers.SerializerMethodField()
    # date_joined = serializers.SerializerMethodField()
    # # total_saved_posts = serializers.SerializerMethodField()
    # # current_city = serializers.SerializerMethodField()
    # # relationship_status = serializers.SerializerMethodField()
    # # user_work_place = serializers.SerializerMethodField()
    # # user_high_school = serializers.SerializerMethodField()
    # # user_lived_place = serializers.SerializerMethodField()
    # # user_activity = serializers.SerializerMethodField()
    # social_account = serializers.SerializerMethodField()
    # social_platform = serializers.SerializerMethodField()

    # def get_current_city(self, obj):
    #     try:
    #         current_city = UserPlacesLived.objects.filter(profile=obj, is_deleted=False, currently_living=True).order_by('-moved_in')[0]
    #         return UserPlacesLivedSerializer(current_city).data
    #     except:
    #         return None

    # def get_first_name(self, obj):
    #     return User.objects.get(profile_user=obj).first_name

    # def get_last_name(self, obj):
    #     return User.objects.get(profile_user=obj).last_name

    # def get_username(self, obj):
    #     return User.objects.get(profile_user=obj).username

    # def get_is_admin(self, obj):
    #     is_admin = False
    #     user = User.objects.get(profile_user=obj)
    #     if user.is_admin == True:
    #         is_admin = True
    #         return is_admin
    #     else:
    #         return is_admin

    # def get_social_account(self, obj):
    #     if obj:
    #         user = Profile.objects.get(user=obj.user).user
    #         if user.social_account:
    #             return True
    #         else:
    #             return False

    # def get_social_platform(self, obj):
    #     if obj:
    #         user = Profile.objects.get(user=obj.user).user
    #         if user.social_platform == 'Google':
    #             return 'Google'
    #         elif user.social_platform == 'Facebook':
    #             return 'Facebook'
    #         else:
    #             return None
    
    # def get_maiden_name(self, obj):
    #     return User.objects.get(profile_user=obj).maiden_name
    
    # def get_mobile_number(self, obj):
    #     return User.objects.get(profile_user=obj).mobile_number

    # def get_email(self, obj):
    #     return User.objects.get(profile_user=obj).email

    # def get_profile_picture(self, obj):
    #     try:
    #         profile_picture = UserProfilePicture.objects.get(profile=obj).picture.picture.url
    #         profile_picture = str(profile_picture.replace("/media/", settings.S3_BUCKET_LINK))
    #     except:
    #         profile_picture = None
    #     return profile_picture

    # def get_cover_picture(self, obj):
    #     try:
    #         cover_picture = UserCoverPicture.objects.get(profile=obj).cover.cover.url
    #         cover_picture = str(cover_picture.replace("/media/", settings.S3_BUCKET_LINK))
    #     except Exception as e:
    #         cover_picture = None
    #     return cover_picture

    # def get_request_sent(self, prof_obj):
    #     try:
    #         profile = self.context['profile']
    #         obj = FriendRequest.objects.get(req_sender=profile,
    #                             req_receiver=prof_obj,
    #                             is_active=True,
    #                             status="Pending"
    #                     )
    #         request_sent = True
    #     except:
    #         request_sent = False
    #     return request_sent

    # def get_request_received(self, prof_obj):
    #     try:
    #         profile = self.context['profile']
    #         obj = FriendRequest.objects.get(req_sender=prof_obj,
    #                             req_receiver=profile,
    #                             is_active=True,
    #                             status="Pending"
    #                     )
    #         request_received = True
    #     except:
    #         request_received = False
    #     return request_received

    # def get_request_id(self, prof_obj):
    #     request_id = None
    #     try:
    #         profile = self.context['profile']
    #         obj = FriendRequest.objects.get(req_sender=prof_obj,
    #                             req_receiver=profile,
    #                             is_active=True,
    #                             status="Pending"
    #                     )
    #         request_id = obj.id
    #     except:
    #         pass
    #     try:
    #         obj = FriendRequest.objects.get(req_sender=profile,
    #                             req_receiver=prof_obj,
    #                             is_active=True,
    #                             status="Pending"
    #                     )
    #         request_id = obj.id
    #     except:
    #         pass
    #     return request_id

    # def get_is_friend(self, prof_obj):
    #     try:
    #         profile = self.context['profile']
    #         obj = FriendsList.objects.get(profile=profile)
    #         if prof_obj in obj.friends.all():
    #             is_friend = True
    #         else:
    #             is_friend = False
    #     except:
    #         is_friend = False
    #     return is_friend

    # def get_has_followed(self, prof_obj):
    #     try:
    #         profile = self.context['profile']
    #         obj = FriendsList.objects.get(profile=profile)
    #         if prof_obj in obj.following.all():
    #             has_followed = True
    #         else:
    #             has_followed = False
    #     except:
    #         has_followed = False
    #     return has_followed


    # def get_followed_by(self, prof_obj):
    #     try:
    #         profile = self.context['profile']
    #         obj = FriendsList.objects.get(profile=profile)
    #         if prof_obj in obj.followers.all():
    #             followed_by = True
    #         else:
    #             followed_by = False
    #     except:
    #         followed_by = False
    #     return followed_by

    # def get_own_profile(self, prof_obj):
    #     try:
    #         profile = self.context['profile']
    #         if prof_obj == profile:
    #             own_profile = True
    #         else:
    #             own_profile = False
    #     except Exception as e:
    #         print(e)
    #         own_profile = False
    #     return own_profile

    # def get_mutual_friends(self, prof_obj):
    #     try:
    #         profile2 = self.context['profile']
    #         f1_list = FriendsList.objects.get(profile=prof_obj)
    #         friends1 = f1_list.friends.all()
    #     except:
    #         friends1 = []

    #     try:
    #         f2_list = FriendsList.objects.get(profile=profile2)
    #         friends2 = f2_list.friends.all()
    #     except:
    #         friends2 = []

    #     mutual_list = list(set(friends1).intersection(friends2))

    #     return GetUserProfileSerializer(mutual_list, many=True).data

    # def get_total_views(self, obj):
    #     return ProfileView.objects.filter(profile=obj).count()

    # def get_total_posts(self, obj):
    #     return Post.objects.filter(profile=obj, is_deleted=False, is_hidden=False).count()

    # def get_privacy_flags(self, prof_obj):
    #     try:
    #         privacy_obj = UserPrivacySettings.objects.get(profile=prof_obj)
    #         return UserPrivacySettingsSerializer(privacy_obj).data
    #     except:
    #         return {}

    # def get_date_joined(self, obj):
    #     return obj.user.date_joined

    # def get_total_saved_posts(self, obj):
    #     return SavedPost.objects.filter(profile=obj, post__is_deleted=False, post__is_hidden=False).count()

    # def get_relationship_status(self, obj):
    #     visited_profile = self.context.get('visited_profile')
    #     try:
    #         relationship = RelationshipStatus.objects.filter(profile=visited_profile, is_deleted=False).order_by('-created_at')[0]
    #     except Exception as e:
    #         print(e)
    #         relationship = None
    #     return RelationshipSerializer(relationship).data

    # def get_user_work_place(self, obj):
    #     visited_profile = self.context.get('visited_profile')
    #     try:
    #         work = UserWorkPlace.objects.filter(profile=visited_profile, is_deleted=False).order_by('-created_at')
    #     except Exception as e:
    #         print(e)
    #         work = None
    #     return UserWorkPlaceSerializer(work, many=True).data
    
    # def get_user_high_school(self, obj):
    #     visited_profile = self.context.get('visited_profile')
    #     try:
    #         high_school = UserHighSchool.objects.filter(profile=visited_profile, is_deleted=False).order_by('-created_at')
    #     except Exception as e:
    #         print(e)
    #         high_school = None
        # return UserHighSchoolSerializer(high_school, many=True).data

    # def get_user_lived_place(self, obj):
    #     profile = self.context.get('profile')
    #     try:
    #         user_lived_place = UserPlacesLived.objects.filter(profile=profile, is_deleted=False).order_by('-created_at')[:1]
    #     except Exception as e:
    #         user_lived_place = None
    #     return UserPlacesLivedSerializer(user_lived_place, many=True).data

    # def get_user_activity(self, obj):
    #     profile = self.context.get('profile')
    #     try:
    #         user_activity = UserActivity.objects.get(profile=profile, is_deleted=False)
    #     except Exception as e:
    #         user_activity = None
    #     return UserActivitySerializer(user_activity).data
    
     
        
    # class Meta:
    #     model = Profile
    #     fields = ['id', 'first_name', 'last_name', 'is_admin','profile_picture', 'username','mobile_number',
    #               'email', 'date_joined', 'street_adress', 'social_account', 'social_platform']
                     
                     
class RequestUserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer to serializer the Profile Object for a friend request object.
    """
    profile = serializers.SerializerMethodField()

    class Meta:
        model = FriendRequest
        # fields = ['id', 'first_name', 'last_name', 'profile_picture', 'cover_picture',
        #           'username', 'email', 'birth_date', 'bio']
        fields = ['id', 'profile']

    def get_profile(self, obj):
        return GetUserProfileSerializer(obj.req_sender).data


class SenderUserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer to serialize the sender profile object in a friend request.
    """

    profile = serializers.SerializerMethodField()

    class Meta:
        model = FriendRequest
        fields = ['id', 'profile']

    def get_profile(self, obj):
        return GetUserProfileSerializer(obj.req_receiver).data


class UserProfileDetaialsSerializer(serializers.ModelSerializer):
    """
    Serializer to serialize the details of Profile Object.
    """
    relationship_status = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    maiden_name = serializers.SerializerMethodField()
    mobile_number = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name', 'maiden_name', 'mobile_number', 'bio', 'street_adress',
                'birth_date','relationship_status', 'current_city',
                'home_town', 'religious_view','political_view', 'birth_place',
                'language', 'alter_mobile', 'website', 'skype', 'facebook', 'google', 'twitter', 'linkedin', 'gender']

    def get_relationship_status(self, obj):
        try:
            relationship = RelationshipStatus.objects.filter(profile=obj, is_deleted=False).order_by('-created_at')[0]
        except Exception as e:
            print(e)
            relationship = ''
        return RelationshipSerializer(relationship).data

    def get_first_name(self, obj):
        return User.objects.get(profile_user=obj).first_name

    def get_last_name(self, obj):
        return User.objects.get(profile_user=obj).last_name


class UserAlbumMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAlbumMedia
        fields = '__all__'


class DefaultUserAlbumSerializer(serializers.ModelSerializer):
    """
    Get minimal data for a user album.
    """
    class Meta:
        model = UserAlbum
        fields = ['id', 'profile', 'album_title', 'privacy']


class GetUserAlbumMediaSerializer(serializers.ModelSerializer):
    """
    Serializer the Album Media
    """
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    vid_thumbnail = serializers.SerializerMethodField()
    album = DefaultUserAlbumSerializer()
    class Meta:
        model = UserAlbumMedia
        fields = ['id', 'album', 'image', 'video', 'vid_thumbnail', 'post', 'description']

    def get_image(self, obj):
        if obj.image:
            return f"{settings.S3_BUCKET_LINK}{obj.image}"
        else:
            return None

    def get_video(self, obj):
        if obj.video:
            return f"{settings.S3_BUCKET_LINK}{obj.video}"
        else:
            return None

    def get_vid_thumbnail(self, obj):
        if obj.vid_thumbnail:
            return f"{settings.S3_BUCKET_LINK}{obj.vid_thumbnail}"
        else:
            return None
        

class GetUserAlbumSerializer(serializers.ModelSerializer):
    """
    Serialize the user album object.
    """
    media = serializers.SerializerMethodField()
    
    class Meta:
        model = UserAlbum
        fields = ['id', 'profile', 'album_title', 'description', 'privacy', 'media']

    def get_media(self, album):
        album_media = UserAlbumMedia.objects.filter(post__is_deleted=False, album=album, is_deleted=False).order_by('-created_at')
        return GetUserAlbumMediaSerializer(album_media, many=True).data


class UserAlbumSerializer(serializers.ModelSerializer):
    """
    Serializer to create the User Album with the media.
    """
    images = serializers.ListField(required=False, allow_null=True,
                                       child=serializers.FileField(
                                           max_length=1000000, allow_empty_file=True, use_url=False
                                       ))
    videos = serializers.ListField(required=False, allow_null=True,
                                       child=serializers.FileField(
                                           max_length=1000000, allow_empty_file=True, use_url=False
                                       ))
    class Meta:
        model = UserAlbum
        fields = '__all__'

    def create(self, validated_data):
        """
        Overridding of the default create method in a Serializer
        Some of the main functions/validations are as follows:
        - Create User Album
        - Create User Album Media with every media file
        - Create separate posts for every album media
        - Create a post for Album as well to show in the newsfeed.
        """

        try:
            image = validated_data.pop('images')
        except:
            image = None
        try:
            video = validated_data.pop('videos')
        except:
            video = None
        if image == None and video == None:
            error = serializers.ValidationError(
                {'success': False, 'response': {'message': 'Please enter media.'}})
            error.status_code = 400
            raise error
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
            album_title = validated_data.pop('album_title')
        except:
            album_title = None
        try:
            description = validated_data.pop('description')
        except:
            description = None
        try:
            privacy = validated_data.pop('privacy')
        except:
            privacy = None
        album = UserAlbum.objects.create(
            profile=user,
            album_title=album_title,
            description=description,
            privacy=privacy,
            is_deleted=False,
        )
        post = Post.objects.create(
                profile=user,
                normal_post=True,
                album_post=True,
                privacy=album.privacy,
            )
        albumpost = AlbumPost.objects.create(
                post=post,
                album=album,
            )
        if image is not None:
            for i in image:
                name = i.name.split('.')
                if name[-1].strip() in ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG']:
                    album_media = UserAlbumMedia.objects.create(
                        album=album,
                        image=i,
                    )
                    album_media.save()
                    album_post = Post.objects.create(
                            profile=user,
                            normal_post=False,
                            album_post=True
                        )
                    album_media.post = album_post
                    album_media.save()
                    albumpost.media_posts.add(album_post)
                    albumpost.save()
                else:
                    raise serializers.ValidationError({'success': False,
                                                         'response': {
                                                             'message': 'Error in image field,'
                                                                        'Only these formats are allowed {}'.format(
                                                                 ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG'])}})
        if video is not None:
            for i in video:
                try:
                    name = i.name.split('.')
                    if name[-1].strip() in ['mp4', 'mkv', 'webm', 'avi', 'flv', 'wmv', 'mov', 'MP4', 'MKV', 'WEBM', 'AVI', 'FLV', 'WMV', 'MOV']:
                        album_media = UserAlbumMedia.objects.create(
                            album=album,
                            video=i,
                        )
                        album_post = Post.objects.create(
                                profile=user,
                                normal_post=False,
                                album_post=True
                            )
                        album_media.post = album_post
                        album_media.save()
                        albumpost.media_posts.add(album_post)
                        albumpost.save()
                    else:
                        raise serializers.ValidationError({'success': False,
                                                             'response': {
                                                                 'message': 'Error in video field,'
                                                                            'Only these formats are allowed {}'.format(
                                                                     ['mp4', 'mkv', 'webm', 'avi', 'flv', 'wmv', 'mov', 'MP4', 'MKV', 'WEBM', 'AVI', 'FLV', 'WMV', 'MOV'])}})
                except Exception as e:
                    print(e)
        return album


class DefaultUserAlbumMediaSerializer(serializers.ModelSerializer):
    """
    Serializer to get the minimal response for a user album media object
    """
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    vid_thumbnail = serializers.SerializerMethodField()
    class Meta:
        model = UserAlbumMedia
        fields = ['id', 'image', 'video', 'vid_thumbnail', 'post', 'description']

    def get_image(self, obj):
        if obj.image:
            return f"{settings.S3_BUCKET_LINK}{obj.image}"
        else:
            return None

    def get_video(self, obj):
        if obj.video:
            return f"{settings.S3_BUCKET_LINK}{obj.video}"
        else:
            return None

    def get_vid_thumbnail(self, obj):
        if obj.vid_thumbnail:
            return f"{settings.S3_BUCKET_LINK}{obj.vid_thumbnail}"
        else:
            return None


class GetAlbumPostSerializer(serializers.ModelSerializer):
    """
    Serialize the media posts and album for a given Album Post.
    - This send the data with the album medias that are included in that album post.
    """
    media_posts = serializers.SerializerMethodField()
    album = DefaultUserAlbumSerializer()

    def get_media_posts(self, obj):
        try:
            posts = obj.media_posts.all()
            medias = UserAlbumMedia.objects.filter(post__in=posts)
            return DefaultUserAlbumMediaSerializer(medias, many=True).data
        except Exception as e:
            return e

    class Meta:
        model = AlbumPost
        fields = ['album', 'media_posts']
        read_only_fields = fields


class UserFamilyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFamilyMember
        fields = ('id', 'profile', 'relation', 'family_member')


class UserLifeEventSerializer(serializers.ModelSerializer):
    user = serializers.CharField(max_length=64, allow_null=False)
    category = serializers.CharField(allow_null=False)
    title = serializers.CharField(allow_null=False, allow_blank=False)
    description = serializers.CharField(allow_null=True, allow_blank=True)
    date = serializers.DateField(allow_null=False)

    class Meta:
        model = UserLifeEvent
        fields = '__all__'

    def create(self, validated_data):
        user = Profile.objects.get(id=validated_data['user'])
        if not user:
            raise serializers.ValidationError("user not found!")
        life_event = UserLifeEvent.objects.create(profile=user,
                                                  category=UserLifeEventCategory.objects.get(
                                                      id=validated_data['category']),
                                                  title=validated_data['title'],
                                                  description=validated_data['description'],
                                                  date=validated_data['date']
                                                  )
        return life_event

    def to_representation(self, data):
        return {'id': data.id,
                'user_id': data.user.id,
                'category': data.category.category_name,
                'title': data.title,
                'description': data.description,
                'date': data.date,
                'created_at': data.created_at,
                'updated_at': data.updated_at,
                }

    def update(self, instance, validated_data):
        instance.category = UserLifeEventCategory.objects.get(id=validated_data['category'])
        instance.title = validated_data['title']
        instance.description = validated_data['description']
        instance.date = validated_data['date']
        instance.updated_at = datetime.datetime.now()
        instance.save()
        return instance


class UserLifeEventCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(allow_null=False, allow_blank=False)

    class Meta:
        model = UserLifeEventCategory
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.category_name = validated_data['category_name']
        instance.updated_at = datetime.datetime.now()
        instance.save()
        return instance


class UserWorkPlaceSerializer(serializers.ModelSerializer):
    """
    Serializer to get and create UserWorkPlace
    """
    class Meta:
        model = UserWorkPlace
        fields = '__all__'


class UserPlacesLivedSerializer(serializers.ModelSerializer):
    """
    Serializer to create USerPlacesLived object
    """
    class Meta:
        model = UserPlacesLived
        fields = '__all__'


class GetUserPlacesLivedSerializer(serializers.ModelSerializer):
    """
    Serialize the UserPlacesLived Object
    """

    class Meta:
        model = UserPlacesLived
        fields = [
                'id', 'profile', 'address', 'country', 'state', 'city',
                'zip_code', 'moved_in', 'moved_out', 'currently_living',
                'privacy', 'created_at', 'updated_at', 'is_deleted']
    

class UserUniversitySerializer(serializers.ModelSerializer):
    """
    Serializer to get or create UserUniversity object.
    """
    class Meta:
        model = UserUniversity
        fields = '__all__'


class UserHighSchoolSerializer(serializers.ModelSerializer):
    """
    Serializer to get or create UserHighSchool object.
    """
    class Meta:
        model = UserHighSchool
        fields = '__all__'    


class RelationshipSerializer(serializers.ModelSerializer):
    """
    Serializer for RelationshipStatus CRUDs.
    """
    class Meta:
        model = RelationshipStatus
        fields = ('id', 'profile', 'relationship', 'partner', 'privacy', 'since')

    def to_representation(self, obj):
        if obj.relationship:
            relationship = obj.relationship.relationship_type
        else:
            relationship = None
        return {
                'id': obj.id,
                'type': relationship,
                'profile': obj.profile.id,
                'partner': obj.partner,
                'privacy': obj.privacy,
                'since': obj.since,
                }


class RelationshipsSerializer(serializers.ModelSerializer):
    """
    Serialize the Relationship object.
    """
    class Meta:
        model = Relationship
        fields = ('id', 'relationship_type')


class UserPrivacySettingsSerializer(serializers.ModelSerializer):
    """
    Serialize UserPrivacySettings object's CRUDs
    """
    class Meta:
        model = UserPrivacySettings
        fields = '__all__'


# Friends module serializer
class FriendRequestSerializer(serializers.ModelSerializer):
    """
    Serializer to Create FriendRequest object.
    """

    class Meta:
        model = FriendRequest
        fields = ['id', 'req_sender', 'req_receiver']


# Notification Serializers
class NotificationSerializer(serializers.ModelSerializer):
    """
    Serialize Notification Object.
    """
    
    profile = serializers.SerializerMethodField()
    page = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    group_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = '__all__'

    def get_profile(self, obj):
        return serialized_post_profile(obj.profile)

    
    def get_page(self, obj):
        if obj.page:
            return obj.page.slug
        else:
            return None

    
    def get_group(self, obj):
        if obj.group:
            return obj.group.slug
        else:
            return None

    
    def get_group_id(self, obj):
        if obj.group:
            return obj.group.id
        else:
            return None


# FCM Device Serializer
class FCMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = ['name', 'device_id', 'registration_id', 'type']


class ProfileStorySerializer(serializers.ModelSerializer):
    """
    Serializer to create ProfileStory object.
    """
    class Meta:
        model = ProfileStory
        fields = '__all__'
        read_only_fields = ['except_friends']


class StoryViewSerializer(serializers.ModelSerializer):
    """
    Serialize all the StoryView objects
    """

    profile = DefaultProfileSerializer()
    reaction = serializers.SerializerMethodField()

    def get_reaction(self, obj):
        try:
            reaction = PostReaction.objects.get(post=obj.story.post, profile=obj.profile)
            return PostReactionSerializer(reaction).data
        except Exception as e:
            return None

    class Meta:
        model = StoryView
        fields = ['reaction', 'profile', 'created_at']


class GetSingleProfileStorySerializer(serializers.ModelSerializer):
    """
    Detailed serialized object of the UserStory
    """
    profile = serializers.SerializerMethodField()
    media_image = serializers.SerializerMethodField()
    media_video = serializers.SerializerMethodField()
    video_thumbnail = serializers.SerializerMethodField()
    post_id = serializers.SerializerMethodField()
    reactions = serializers.SerializerMethodField()
    views = serializers.SerializerMethodField()
    total_views = serializers.SerializerMethodField()
    except_friends = GetUserProfileSerializer(read_only=True , many=True)
    class Meta:
        model = ProfileStory
        fields = ['id', 'profile', 'text', 'font_family', 'background_color',
                  'text_color', 'media_image', 'media_video', 'video_thumbnail', 'x_axis', 'y_axis', 'angle', 'story_type', 'created_at', 'privacy',
                  'post_id', 'reactions', 'views', 'total_views', 'except_friends']
        read_only_fields = ['except_friends']

    def get_profile(self, obj):
        return serialized_post_profile(obj.profile)

    def get_media_image(self, obj):
        if obj.story_type == 'Media':
            if obj.media_image:
                media = f"{settings.S3_BUCKET_LINK}{obj.media_image}"
            else:
                media = None
        else:
            media = None
        return media

    def get_video_thumbnail(self, obj):
        if obj.story_type == 'Media':
            if obj.video_thumbnail:
                media = f"{settings.S3_BUCKET_LINK}{obj.video_thumbnail}"
            else:
                media = None
        else:
            media = None
        return media

    def get_media_video(self, obj):
        if obj.story_type == 'Media':
            if obj.media_video:
                media = f"{settings.S3_BUCKET_LINK}{obj.media_video}"
            else:
                media = None
        else:
            media = None
        return media

    def get_post_id(self, obj):
        try:
            return obj.post.id
        except:
            return None

    def get_reactions(self, obj):
        try:
            return PostReactionSerializer(obj.post.postreaction_set.all(), many=True).data
        except:
            return None

    def get_views(self, obj):
        return StoryViewSerializer(obj.storyview_set.all(), many=True).data
    
    def get_total_views(self, obj):
        return obj.storyview_set.all().count()


class ContactInforSerializer(serializers.ModelSerializer):
    """
    Create the ContactInfo of a Profile
    """

    class Meta:
        model = Profile
        fields = ['alter_mobile', 'skype', 'website']


class UserActivitySerializer(serializers.ModelSerializer):
    """
    Create the UserActivity of a Profile
    """
    class Meta:
        model = UserActivity
        fields = '__all__'


class GetUserActivitySerializer(serializers.ModelSerializer):
    """
    Get the serialized object of the UserActivity object.
    """

    profile = serializers.SerializerMethodField()
    class Meta:
        model = UserActivity
        fields = ['id', 'profile', 'activity', 'interest', 'favorite_music', 'favorite_movie', 'favorite_tv_show', 'favorite_book', 'favorite_game', 'favorite_quote', 'about_me', 'is_deleted', 'created_at', 'updated_at']
    
    def get_profile(self, obj):
        user = self.context.get('user')
        try:
            profile = Profile.objects.get(user=user, user__is_active=True, is_deleted=False)
            print(profile)
            return DefaultProfileSerializer(profile).data
        except:
            return None


class ReportProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportProfile
        fields = '__all__'


class GetReportProfileCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportProfileCategory
        fields = '__all__'


class ProgressUserProfileSerializer(serializers.ModelSerializer):

    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()


    def get_first_name(self, obj):
        return User.objects.get(profile_user=obj).first_name

    def get_last_name(self, obj):
        return User.objects.get(profile_user=obj).last_name

    def get_username(self, obj):
        return User.objects.get(profile_user=obj).username

    def get_email(self, obj):
        return User.objects.get(profile_user=obj).email

    def is_valid_queryparam_progress(*args):
        return args != '' and args is not None

    def get_progress(self, obj):
        user = User.objects.get(profile_user=obj, is_active=True)
        profile = Profile.objects.get(user=user, is_deleted=False)
        try:
            profile_picture = UserProfilePicture.objects.get(profile=obj).picture.picture
        except:
            profile_picture = None
        try:
            cover_picture = UserCoverPicture.objects.get(profile=obj).cover.cover
        except Exception as e:
            cover_picture = None

        try:
            relationship = RelationshipStatus.objects.filter(profile=obj, is_deleted=False).order_by('-created_at')[0]
        except Exception as e:
            relationship = None

        try:
            current_city = UserPlacesLived.objects.filter(profile=obj, is_deleted=False, currently_living=True).order_by('-created_at')[0]
        except:
            current_city =  None

        try:
            work = UserWorkPlace.objects.filter(profile=obj, is_deleted=False).order_by('-created_at')[0]
        except Exception as e:
            work = None

        try:
            high_school = UserHighSchool.objects.filter(profile=obj, is_deleted=False).order_by('-created_at')[0]
        except Exception as e:
            high_school = None

        try:
            user_lived_place = UserPlacesLived.objects.filter(profile=obj, is_deleted=False)
        except Exception as e:
            user_lived_place = None
            
        try:
            user_activity = UserActivity.objects.get(profile=obj, is_deleted=False)
        except Exception as e:
            user_activity = None
        try:
            mobile = User.objects.get(profile_user=obj, is_active=True).mobile_number
        except Exception as e:
            mobile = None

        my_dict = dict()
        if mobile !=None and mobile !='':
                my_dict["mobile"] = mobile

        if profile_picture !=None and profile_picture !='':
                my_dict["profile_picture"] = profile_picture

        if cover_picture !=None and cover_picture !='':
                my_dict["cover_picture"] = cover_picture

        if relationship !=None and relationship !='':
                my_dict["relationship"] = relationship

        if current_city !=None and current_city !='':
                my_dict["current_city"] = current_city

        if work !=None and work !='':
                my_dict["work"] = work

        if high_school !=None and high_school !='':
                my_dict["high_school"] = high_school

        if user_lived_place !=None and user_lived_place !='':
                my_dict["user_lived_place"] = user_lived_place

        if user_activity !=None and user_activity !='':
                my_dict["user_activity"] = user_activity
        
        if self.is_valid_queryparam_progress(my_dict):
            if len(my_dict) < 1:
                percentage = 55
            else:

                percentage = 55 + (len(my_dict)*5)
                percentage = str(percentage) + '%'
            return percentage
    class Meta:
        model = Profile
        fields = ['id', 'progress','first_name', 'last_name', 'email', 'username']
      
class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = [
                'id' ,'profile', 'name', 'about', 'company_type',
                'license_number', 'email', 'phone', 'dial_code', 'country', 'state', 'city', 
                'street_address', 'longitude','latitude'
                ] 

