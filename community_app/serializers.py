from tokenize import group
from . models import *
from youonline_social_app.models import *
import datetime
from rest_framework import serializers
from rest_framework import status
from . import views
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
import random, string
from youonline_social_app.serializers import users_serializers
from youonline_social_app.serializers import post_serializers


# Group Serializers
class GroupCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupCategory
        fields = ['id', 'title']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class GetGroupSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    is_requested = serializers.SerializerMethodField()
    is_invited = serializers.SerializerMethodField()
    banner = serializers.SerializerMethodField()
    total_members = serializers.SerializerMethodField()
    friends = serializers.SerializerMethodField()

    def get_category(self, obj):
        return GroupCategorySerializer(obj.category).data

    def get_created_by(self, obj):
        return post_serializers.DefaultProfileSerializer(obj.created_by).data

    def get_is_admin(self, obj):
        try:
            profile = self.context['profile']
            obj = GroupMember.objects.get(profile=profile,
                                group=obj,
                                is_admin=True,
                        )
            is_admin = True
        except:
            is_admin = False
        return is_admin

    def get_is_member(self, obj):
        try:
            profile = self.context['profile']
            obj = GroupMember.objects.get(profile=profile,
                                group=obj,
                        )
            is_member = True
        except:
            is_member = False
        return is_member

    def get_friends(self, obj):
        try:
            profile = self.context['profile']
            group_friends = list(GroupMember.objects.filter(group=obj).exclude(profile=profile).values_list('profile__id', flat=True))
            friends_list = FriendsList.objects.get(profile=profile).friends.all().values_list('id', flat=True)
            mutual_list = list(set(group_friends).intersection(friends_list))
            profiles = Profile.objects.filter(id__in=mutual_list)
            friends = post_serializers.DefaultProfileSerializer(profiles, many=True).data
        except:
            return None
        
        return friends

    def get_is_requested(self, obj):
        try:
            profile = self.context['profile']
            obj = GroupRequest.objects.get(profile=profile,
                                group=obj,
                                status='Pending',
                                is_active=True,
                        )
            is_requested = True
        except:
            is_requested = False
        return is_requested

    def get_is_invited(self, obj):
        try:
            profile = self.context['profile']
            obj = GroupInvite.objects.get(profile=profile,
                                        group=obj,
                                        is_active=True,
                        )

            is_invited = True
        except Exception as e:
            is_invited = False
        return is_invited

    def get_banner(self, obj):
        try:
            banner = GroupCurrentBanner.objects.get(group=obj).banner.banner
            print(banner)
            banner = f"{settings.S3_BUCKET_LINK}{banner}"
        except Exception as e:
            banner = None
        return banner

    def get_total_members(self, obj):
        return GroupMember.objects.filter(group=obj).count()

    class Meta:
        model = Group
        fields = ['id', 'name', 'category', 'privacy', 'description', 'created_at', 'banner', 'slug', 'created_by',
                'is_admin', 'is_member', 'is_requested', 'is_invited', 'is_hidden', 'total_members', 'friends', 'approval_required', 'who_can_post']


class DefaultGroupSerializer(serializers.ModelSerializer):
    banner = serializers.SerializerMethodField()
    category = GroupCategorySerializer()

    class Meta:
        model = Group
        fields = ['id', 'name', 'privacy', 'category', 'banner', 'slug', 'created_by']

    def get_banner(self, obj):
        try:
            banner = GroupCurrentBanner.objects.get(group=obj).banner.banner
            banner = f"{settings.S3_BUCKET_LINK}{banner}"
        except Exception as e:
            banner = None
        return banner
    
    

class GroupRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupRequest
        fields = ['id', 'profile', 'group', 'status', 'created_at']


class GetGroupRequestSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    class Meta:
        model = GroupRequest
        fields = ['id', 'profile', 'group', 'status', 'created_at']

    def get_profile(self, obj):
        return post_serializers.DefaultProfileSerializer(obj.profile).data

    def get_group(self, obj):
        return GroupSerializer(obj.group).data


class GroupMemberSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    
    class Meta:
        model = GroupMember
        fields = ['id', 'profile', 'group', 'is_admin', 'date_joined', 'approved_by']

    def get_profile(self, obj):
        return post_serializers.DefaultProfileSerializer(obj.profile).data

    def get_group(self, obj):
        return GroupSerializer(obj.group).data


class GroupRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupRule
        fields = '__all__'


class GroupInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupInvite
        fields = '__all__'


class GetGroupInviteSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    invited_by = serializers.SerializerMethodField()
    class Meta:
        model = GroupInvite
        fields = ['id', 'profile', 'group', 'invited_by', 'created_at']

    def get_profile(self, obj):
        return post_serializers.DefaultProfileSerializer(obj.profile).data

    def get_invited_by(self, obj):
        return post_serializers.DefaultProfileSerializer(obj.invited_by).data

    def get_group(self, obj):
        try:
            profile = self.context.get("profile")
            group = Group.objects.get(id=obj.group.id, is_deleted=False)
            return GetGroupSerializer(group, context={"profile": profile}).data
        except:
            return None


class GroupBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupBanner
        fields = '__all__'

class GroupLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupLogo
        fields = '__all__'


class GetPostGroupBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupBanner
        fields = ['banner', 'id']

    def to_representation(self, obj):
        return_dict = {}
        if obj.banner:
            return_dict["banner"] = f"{settings.S3_BUCKET_LINK}{obj.banner}"
        else:
            return_dict["picture"] = None
        return_dict["id"] = obj.post.id
        return return_dict

class GetPostGroupLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupLogo
        fields = ['logo', 'id']

    def to_representation(self, obj):
        return_dict = {}
        if obj.logo:
            return_dict["logo"] = f"{settings.S3_BUCKET_LINK}{obj.logo}"
        else:
            return_dict["picture"] = None
        return_dict["id"] = obj.post.id
        return return_dict


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = '__all__'


class GetPageSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()
    is_administrator = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    is_editor = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    banner = serializers.SerializerMethodField()
    friends = serializers.SerializerMethodField()
    liked_by = serializers.SerializerMethodField()
    total_follower = serializers.SerializerMethodField()
    is_invited = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ['id', 'name', 'username', 'category', 'privacy', 'description', 'created_at', 'created_by', 'slug', 'is_administrator',
                'owner', 'is_editor', 'total_follower','is_following', 'is_invited', 'is_hidden', 'total_likes', 'banner', 'friends', 'liked_by', 'street_adress']

    def get_category(self, obj):
        return GroupCategorySerializer(obj.category).data

    def get_created_by(self, obj):
        return post_serializers.DefaultProfileSerializer(obj.created_by).data


    def get_friends(self, obj):
        try:
            profile = self.context['profile']
            page_frineds = list(PageFollower.objects.filter(page=obj).exclude(profile=profile).values_list('profile__id', flat=True))
            friends_list = FriendsList.objects.get(profile=profile).friends.all().values_list('id', flat=True)
            mutual_list = list(set(page_frineds).intersection(friends_list))
            profiles = Profile.objects.filter(id__in=mutual_list)
            return post_serializers.DefaultProfileSerializer(profiles, many=True).data
        except Exception as e:
            return None

    def get_liked_by(self, obj):
        liked_by = PageFollower.objects.filter(page=obj)
        return PageFollowerSerializer(liked_by, many=True).data

    def get_is_following(self, obj):
        try:
            profile = self.context['profile']
            obj = PageFollower.objects.get(profile=profile,
                                page=obj,
                        )
            is_following = True
        except:
            is_following = False
        return is_following

    def get_is_administrator(self, obj):
        try:
            profile = self.context['profile']
            obj = PageFollower.objects.get(
                                page=obj, profile=profile,
                                is_admin=True
                        )
            is_administrator = True
        except:
            is_administrator = False
        return is_administrator

    def get_owner(self, obj):
        try:
            profile = self.context['profile']
            obj = PageFollower.objects.get(
                                page=obj, profile=profile,
                                is_administrator=True
                        )
            owner = True
        except:
            owner = False
        return owner

    def get_is_editor(self, obj):
        try:
            profile = self.context['profile']
            obj = PageFollower.objects.get(profile=profile,
                                page=obj,
                                is_editor=True
                        )
            is_editor = True
        except:
            is_editor = False
        return is_editor


    def get_total_likes(self, obj):
        return PageFollower.objects.filter(page=obj).count()

    def get_total_follower(self, obj):
        return PageFollower.objects.filter(page=obj).count()

    def get_banner(self, obj):
        try:
            banner = PageCurrentBanner.objects.get(page=obj).banner.banner
            banner = f"{settings.S3_BUCKET_LINK}{banner}"
        except Exception as e:
            print(e)
            banner = None
        return banner
    def get_is_invited(self, obj):
        try:
            profile = self.context['profile']
            obj = PageInvite.objects.get(profile=profile,
                                        page=obj,
                                        is_active=True,
                        )

            is_invited = True
        except Exception as e:
            is_invited = False
        return is_invited


class PageFollowerSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    class Meta:
        model = PageFollower
        fields = ['id', 'profile', 'page', 'is_admin', 'date_joined', 'is_administrator', 'is_editor']

    def get_profile(self, obj):
        return post_serializers.DefaultProfileSerializer(obj.profile).data


class DefaultPageSerializer(serializers.ModelSerializer):
    banner = serializers.SerializerMethodField()
    category = GroupCategorySerializer()
    total_likes = serializers.SerializerMethodField()
    
    class Meta:
        model = Page
        fields = ['id', 'name', 'username', 'privacy', 'category', 'banner', 'total_likes', 'slug', 'description', 'created_by']

    def get_banner(self, obj):
        try:
            banner = PageCurrentBanner.objects.get(page=obj).banner.banner
            banner = f"{settings.S3_BUCKET_LINK}{banner}"
        except Exception as e:
            banner = None
        return banner

    def get_total_likes(self, obj):
        return PageFollower.objects.filter(page=obj).count()


class PageRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageRule
        fields = '__all__'


class PageInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageInvite
        fields = '__all__'


class GetPageInviteSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    page = serializers.SerializerMethodField()
    invited_by = serializers.SerializerMethodField()
    class Meta:
        model = PageInvite
        fields = ['id', 'profile', 'page', 'invited_by', 'created_at']

    def get_profile(self, obj):
        return post_serializers.DefaultProfileSerializer(obj.profile).data

    def get_invited_by(self, obj):
        return post_serializers.DefaultProfileSerializer(obj.invited_by).data

    def get_page(self, obj):
        try:
            profile = self.context.get("profile")
            return GetPageSerializer(obj.page, context={"profile": profile}).data
        except:
            return None


class PageBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageBanner
        fields = '__all__'

class PageLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageLogo
        fields = '__all__'


class GetPostPageBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageBanner
        fields = ['banner', 'id']

    def to_representation(self, obj):
        return_dict = {}
        if obj.banner:
            return_dict["banner"] = f"{settings.S3_BUCKET_LINK}{obj.banner}"
        else:
            return_dict["picture"] = None
        return_dict["id"] = obj.post.id
        return return_dict

class GetPostPageLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageLogo
        fields = ['logo', 'id']

    def to_representation(self, obj):
        return_dict = {}
        if obj.logo:
            return_dict["logo"] = f"{settings.S3_BUCKET_LINK}{obj.logo}"
        else:
            return_dict["picture"] = None
        return_dict["id"] = obj.post.id
        return return_dict


