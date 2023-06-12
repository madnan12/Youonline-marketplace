from unicodedata import category
from rest_framework import serializers
from youonline_social_app.models import *
from . models import *
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
import random, string
from moviepy.editor import VideoFileClip
from django.conf import settings
from youonline_social_app.serializers.post_serializers import *
from youonline_social_app.serializers.users_serializers import *
from youonline_social_app.serializers.utility_serializers import *
from job_app.serializers import *
import json


class SubSubCategorySerializer(serializers.ModelSerializer):
    total_count = serializers.SerializerMethodField()

    def get_total_count(self, obj):
        properties = Property.objects.filter(sub_sub_category=obj, is_deleted=False, verification_status='Verified').count()
        return properties
    class Meta:
        model = SubSubCategory
        fields = ['id', 'title', 'total_count']


class SubCategorySerializer(serializers.ModelSerializer):
    sub_sub_category = SubSubCategorySerializer(many=True)
    total_count = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            return f"{settings.DOMAIN_NAME}{obj.image.url}"
        else:
            return None
    def get_total_count(self, obj):
        properties = Property.objects.filter(sub_category=obj, is_deleted=False, verification_status='Verified').count()
        return properties

    class Meta:
        model = SubCategory
        fields = ['id', 'title', 'sub_sub_category', 'total_count', 'image']


class CategorySerializer(serializers.ModelSerializer):
    sub_category = serializers.SerializerMethodField()
    total_count = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            return f"{settings.DOMAIN_NAME}{obj.image.url}"

    def get_total_count(self, obj):
        properties = Property.objects.filter(category=obj, is_deleted=False, is_active=True).count()
        return properties

    def get_sub_category(self, obj):
        sub_category = SubCategory.objects.filter(category=obj)
        return SubCategorySerializer(sub_category, many=True).data

    class Meta:
        model = Category
        fields = ['id', 'title', 'sub_category', 'total_count', 'image']


class DetailCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class DetailSubCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = SubCategory
        fields = ['id', 'title']


class DetailSubSubCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = SubSubCategory
        fields = ['id', 'title']


class PostPropertySerializer(serializers.ModelSerializer):
    feature = serializers.ListField(required=False, allow_null=True)
    property_image = serializers.ListField(required=False, allow_null=True,
                                       child=serializers.FileField(
                                           max_length=1000000, allow_empty_file=True, use_url=False
                                       ))
    property_video = serializers.ListField(required=False, allow_null=True,
                                       child=serializers.FileField(
                                           max_length=1000000, allow_empty_file=True, use_url=False
                                       ))
    floor_image = serializers.ListField(required=False, allow_null=True,
                                       child=serializers.FileField(
                                           max_length=1000000, allow_empty_file=True, use_url=False
                                       ))

    class Meta:
        model = Property
        fields = '__all__'

    def create(self, validated_data):
        """
        Override the create method to add custom validation
        - Create a post with every property creation.
        - Validate media formats.
        - Create PropertyMedia objects with every media.
        """
        try:
            use = validated_data['profile']
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
            property_images = validated_data.pop('property_image')
        except:
            property_images = None
        # Condition to check maximum number of images.
        if property_images:
            if len(property_images) > 20:
                error = serializers.ValidationError({'success': False,
                                                     'response': {
                                                         'message': 'You can only upload 10 Images for one Property'}})
                error.status_code = 400
                raise error
        try:
            property_videos = validated_data.pop('property_video')
        except:
            property_videos = None
        # Condition to check maximum number of videos.
        if property_videos:
            if len(property_videos) > 2:
                error = serializers.ValidationError({'success': False,
                                                     'response': {
                                                         'message': 'You can only upload 2 Videos for one Property'}})
                error.status_code = 400
                raise error
        try:
            floor_images = validated_data.pop('floor_image')
        except:
            floor_images = None
        try:
            feature = validated_data.pop('feature')
        except:
            feature = None
        try:
            privacy = validated_data['privacy']
        except:
            privacy = 'Public'

        # items = json.loads(feature[0])

        # def create(self, validated_data):
        property_object = Property.objects.create(**validated_data)
            # for i in range(len(items)):
            #     property_feature = PropertyFeatures.objects.create(
            #         name=items[i]
            #     )
            #     property_object.feature.add(property_feature)
            #     property_object.save()
            # return property_object
        # property_object = create(self, validated_data)

        post = Post.objects.create(
            profile=user,
            privacy=privacy,
            property_post=True
        )
        property_object.post = post
        property_object.save()
        if property_images is not None:
            for i in property_images:
                name = i.name.split('.')
                if name[-1].strip() in ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG']:
                    prop_media = PropertyMedia.objects.create(
                        profile=user,
                        post=post,
                        property=property_object,
                        property_image=i
                    )
                    prop_media.save()
                else:
                     raise serializers.ValidationError({'success': False,
                                                         'response': {
                                                             'message': 'Error in post_image field,'
                                                                        'Only these formats are allowed {}'.format(
                                                                 ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG'])}})
        if floor_images is not None:
            for i in floor_images:
                name = i.name.split('.')
                if name[-1].strip() in ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG']:
                    prop_media = PropertyMedia.objects.create(
                        profile=user,
                        post=post,
                        property=property_object,
                        floor_image=i
                    )
                    prop_media.save()
                else:
                     raise serializers.ValidationError({'success': False,
                                                         'response': {
                                                             'message': 'Error in post_image field,'
                                                                        'Only these formats are allowed {}'.format(
                                                                 ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG'])}})
        if property_videos is not None:
            for video in property_videos:
                name = video.name.split('.')
                if name[-1] in ['mp4', 'mkv', 'webm', 'avi', 'flv', 'wmv', 'mov', 'MP4', 'MKV', 'WEBM', 'AVI', 'FLV', 'WMV', 'MOV']:
                    if video.size > 75000000:
                        error = serializers.ValidationError({'success': False,
                                                             'response': {
                                                                 'message': 'Error in post video size. Maximum allowed size is 75mb.'}})
                        error.status_code = 400
                        raise error
                    else:
                        obj = PropertyMedia(
                                profile=user,
                                property=property_object,
                                post=post,
                                property_video=video
                            )
                        obj.save()
                else:
                    raise serializers.ValidationError({'success': False,
                                                         'response': {
                                                             'message': 'Error in post_video field,'
                                                                        'Only these formats are allowed {}'.format(
                                                                 ['mp4', 'mkv', 'webm', 'avi', 'flv', 'wmv', 'mov', 'MP4', 'MKV', 'WEBM', 'AVI', 'FLV', 'WMV', 'MOV'])}})
        return property_object


class PostPropertyMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyMedia
        fields = ['property_image', 'property_video', 'property_video_thumbnail', 'floor_image']


class PropertyMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyMedia
        fields = ['property_image', 'property_video', 'property_video_thumbnail']

    def to_representation(self, obj):
        return_dict = dict()
        if obj.property_image:
            return_dict['id'] = obj.id
            return_dict['property_image'] = f"{settings.S3_BUCKET_LINK}{obj.property_image}"

        if obj.property_video:
            return_dict['id'] = obj.id
            return_dict['property_video'] = f"{settings.S3_BUCKET_LINK}{obj.property_video}"
            if obj.property_video_thumbnail:
                return_dict['id'] = obj.id
                return_dict['property_video_thumbnail'] = f"{settings.S3_BUCKET_LINK}{obj.property_video_thumbnail}"
            else:
                return_dict['property_video_thumbnail'] = ''

        if obj.floor_image:
            return_dict['id'] = obj.id
            return_dict['floor_image'] = f"{settings.S3_BUCKET_LINK}{obj.floor_image}"
        return return_dict


class PropertyPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'text']


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyFeatures
        fields = '__all__'

class PropertyImageMediaSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.property_image:
            return f"{settings.S3_BUCKET_LINK}{obj.property_image}"
    class Meta:
        model = PropertyMedia
        fields = ['id', 'image']


class PropertyVideoMediaSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()
    video_thumbnail = serializers.SerializerMethodField()

    def get_video(self, obj):
        if obj.property_video:
            return f"{settings.S3_BUCKET_LINK}{obj.property_video}"

    def get_video_thumbnail(self, obj):
        if obj.property_video_thumbnail:
            return f"{settings.S3_BUCKET_LINK}{obj.property_video_thumbnail}"
    class Meta:
        model = PropertyMedia
        fields = ['id','video' , 'video_thumbnail']

class PropertyGetSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    sub_category = serializers.SerializerMethodField()
    image_media = serializers.SerializerMethodField()
    video_media = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    total_saved = serializers.SerializerMethodField()
    deal_data = serializers.SerializerMethodField()

    def get_deal_data(self, property):
        try:
            deal_data = DealData.objects.get(property=property, is_deleted=False)
            return DealDataSerializer(deal_data).data
        except:
            return None

    def get_total_saved(self, property):
        favourite = FavouriteProperty.objects.filter(property=property).count()
        if favourite:
            return favourite
        else:
            return None

    def get_profile(self, property):
        return DefaultProfileSerializer(property.profile, many=False).data

    def get_company(self, property):
        if property.business_type == 'Company':
            try:
                company = Company.objects.get(profile=property.profile, company_type='Property')
                return CompanySerializer(company).data
            except:
                return None

    def get_currency(self, property):
        return CurrencySerializer(property.currency, many=False).data

    def get_category(self, property):
        return DetailCategorySerializer(property.category, many=False).data

    def get_sub_category(self, property):
        return DetailSubCategorySerializer(property.sub_category, many=False).data

    def get_image_media(self, property):
        return PropertyImageMediaSerializer(property.propertymedia_set.filter(is_deleted=False).exclude(property_image=''), many=True).data
    
    def get_video_media(self, property):
        return PropertyVideoMediaSerializer(property.propertymedia_set.filter(is_deleted=False).exclude(property_video=''), many=True).data

    def get_is_favourite(self, obj):
        try:
            profile = self.context.get("profile")
            favourite = FavouriteProperty.objects.get(property=obj, profile=profile, is_deleted=False)
            return True
        except:
            return False

    class Meta:
        model = Property
        fields = ['id', 'profile', 'is_favourite',
                  'category', 'sub_category', 'image_media', 'video_media', 'business_type', 'company',
                  'street_adress', 'longitude', 'latitude', 'dial_code', 'is_active',
                  'name', 'area', 'area_unit', 'bedrooms', 'baths', 'description', 'currency', 'deal_data',
                  'price', 'mobile', 'furnished', 'property_type', 'is_deal', 'view_count', 'total_saved',
                  'duration', 'verification_status', 'is_promoted', 'created_at', 'updated_at', 'slug']


class PropertyUpdateSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    sub_category = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()

    def get_profile(self, property):
        return DefaultProfileSerializer(property.profile, many=False).data

    def get_currency(self, property):
        return CurrencySerializer(property.currency, many=False).data

    def get_category(self, property):
        return DetailCategorySerializer(property.category, many=False).data

    def get_sub_category(self, property):
        return DetailSubCategorySerializer(property.sub_category, many=False).data

    def get_media(self, property):
        return PropertyMediaSerializer(property.propertymedia_set.filter(is_deleted=False), many=True).data

    class Meta:
        model = Property
        fields = ['id', 'profile', 'post', 'category', 'sub_category', 'sub_sub_category',
                  'country', 'state', 'city', 'street_adress', 'longitude', 'latitude',
                  'name', 'area', 'bedrooms', 'baths', 'description', 'currency', 'price', 'mobile', 'email',
                  'living_room', 'balcony', 'lift', 'parking', 'storage', 'gym', 'cinema',
                  'conference', 'swimming_poll', 'maid_room', 'sports',
                  'privacy', 'duration', 'language', 'media', 'slug']


class PropertyListingMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyMedia
        fields = ['property_image']

    def to_representation(self, obj):
        return_dict = dict()
        if obj.property_image:
            return_dict['id'] = obj.id
            return_dict['property_image'] = f"{settings.S3_BUCKET_LINK}{obj.property_image}"
        return return_dict


class PropertyListingSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()

    def get_profile(self, property):
        return DefaultProfileSerializer(property.profile, many=False).data

    def get_currency(self, property):
        return CurrencySerializer(property.currency, many=False).data

    def get_media(self, property):
        return PropertyListingMediaSerializer(property.propertymedia_set.filter(is_deleted=False), many=True).data

    def get_is_favourite(self, obj):
        try:
            profile = self.context.get("profile")
            favourite = FavouriteProperty.objects.get(property=obj, profile=profile, is_deleted=False)
            return True
        except:
            return False

    class Meta:
        model = Property
        fields = [
                'id', 'name', 'currency', 'price', 
                'street_adress', 'profile', 'media', 'created_at', 'is_favourite', 
                'slug', 'description', 'mobile', 'email'
                ]


class PropertyListingFavouriteSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()

    def get_profile(self, property):
        return DefaultProfileSerializer(property.profile, many=False).data

    def get_currency(self, property):
        return CurrencySerializer(property.currency, many=False).data

    def get_country(self, property):
        return CountrySerializer(property.country, many=False).data

    def get_state(self, property):
        return StateSerializer(property.state, many=False).data

    def get_city(self, property):
        return CitySerializer(property.city, many=False).data

    def get_media(self, property):
        return PropertyListingMediaSerializer(property.propertymedia_set.filter(is_deleted=False), many=True).data

    def check_favorite(self, obj):
        return True

    class Meta:
        model = Property
        fields = ['id', 'name', 'currency', 'country', 'state', 'city', 'price',
                  'profile', 'privacy', 'media', 'created_at', 'is_favourite', 'slug']


class PropertyFavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavouriteProperty
        fields = '__all__'


class PropertyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactProperty
        fields = '__all__'


class PropertyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportProperty
        fields = '__all__'

