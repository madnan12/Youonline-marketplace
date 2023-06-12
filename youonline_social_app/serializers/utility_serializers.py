import profile
from attr import fields
from rest_framework import serializers
from youonline_social_app.serializers.users_serializers import UserHighSchoolSerializer, UserActivitySerializer
from ..models import *


"""
Utility serializer to serialize the Utility objects.
"""

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


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name', 'code', 'rtl']

class ExceptionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExceptionRecord
        fields = '__all__'

class DiscoverUserPlacesLivedSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPlacesLived
        fields = '__all__'


class RelationshipStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelationshipStatus
        fields = '__all__'

class DiscoverProfileSerializer(serializers.ModelSerializer):
    """
    This is the default Profile Serializer used to get the basic UserInformation.
    """
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()
    current_city = serializers.SerializerMethodField()
    school = serializers.SerializerMethodField()
    interest = serializers.SerializerMethodField()
    relationship_status = serializers.SerializerMethodField()
    def get_first_name(self, obj):
        return User.objects.get(profile_user=obj).first_name

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

    def get_school(self, obj):
        schools = UserHighSchool.objects.filter(profile=obj)
        serializer = UserHighSchoolSerializer(schools, many=True).data
        return serializer

    def get_profile_picture(self, obj):
        try:
            profile_picture = UserProfilePicture.objects.get(profile=obj).picture.picture.url
            profile_picture = str(profile_picture.replace("/media/", settings.S3_BUCKET_LINK))
        except:
            profile_picture = None
        return profile_picture

    def get_current_city(self, obj):
        try:
            current_city = UserPlacesLived.objects.filter(profile=obj, is_deleted=False, currently_living=True).order_by('-moved_in')[0]
            return DiscoverUserPlacesLivedSerializer(current_city).data
        except:
            return None
    def get_interest(self, obj):
        try:
            activity = UserActivity.objects.get(profile=obj)
            serialzer = UserActivitySerializer(activity)
            return serialzer.data
        except:
            pass
    
    def get_relationship_status(self, obj):
        try:
            relation = RelationshipStatus.objects.get(profile=obj, is_deleted=False, privacy='Public')
            serializer = RelationshipStatusSerializer(relation)
            print(serializer)
            return serializer.data
        except:
            pass
    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name', 'username', 'gender', 'is_admin', 'profile_picture', 'bio', 'birth_date','current_city', 'alter_mobile', 'skype', 'website','school', 'interest', 'relationship_status']
