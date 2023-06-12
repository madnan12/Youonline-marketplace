from email.mime import image
from unicodedata import category
from rest_framework import serializers
from . models import *
from youonline_social_app.models import *
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
import random, string
from moviepy.editor import VideoFileClip
from django.conf import settings
from youonline_social_app.serializers.post_serializers import *
from youonline_social_app.serializers.users_serializers import *
from youonline_social_app.serializers.utility_serializers import *
from job_app.serializers import *


class ClassifiedeMakeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    total_count = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:

            return f"{settings.DOMAIN_NAME}{obj.image.url}"
        else:
            return None

    def get_total_count(self, obj):
        automotives = Classified.objects.filter(make=obj, is_deleted=False, verification_status='Verified').count()
        return automotives
    class Meta:
        model = ClassifiedeMake
        fields = [
            'id',
            'title',
            'image',
            'subcategory',
            'background_color',
            'is_featured',
            'total_count']

class ClassifiedSubSubCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    total_count = serializers.SerializerMethodField()

    def get_total_count(self, obj):
        classifieds = Classified.objects.filter(sub_sub_category=obj, is_deleted=False, is_active=True).count()
        return classifieds

    def get_image(self, obj):
        if obj.image:
            return f"{settings.DOMAIN_NAME}{obj.image.url}"
        else:
            return None
    class Meta:
        model = ClassifiedSubSubCategory
        fields = ['id', 'title', 'image', 'background_color', 'total_count']


class ClassifiedSubCategorySerializer(serializers.ModelSerializer):
    sub_sub_category = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    total_count = serializers.SerializerMethodField()

    def get_sub_sub_category(self, obj):
        sub_sub_category = ClassifiedSubSubCategory(sub_category=obj)
        return ClassifiedSubSubCategorySerializer(many=True).data

    def get_total_count(self, obj):
        classifieds = Classified.objects.filter(sub_category=obj, is_deleted=False, is_active=True).count()
        return classifieds

    def get_image(self, obj):
        if obj.image:
            return f"{settings.DOMAIN_NAME}{obj.image.url}"
        else:
            return None
    class Meta:
        model = ClassifiedSubCategory
        fields = ['id', 'title', 'sub_sub_category', 'image', 'background_color', 'total_count']


class ClassifiedCategorySerializer(serializers.ModelSerializer):
    sub_category = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    total_count = serializers.SerializerMethodField()

    def get_sub_category(self, obj):
        sub_category = ClassifiedSubCategory.objects.filter(category=obj)
        return ClassifiedSubCategorySerializer(sub_category, many=True).data

    class Meta:
        model = ClassifiedCategory
        fields = ['id', 'title', 'sub_category', 'image', 'background_color','business_directory', 'total_count']

    def get_image(self, obj):
        if obj.image:
            return f"{settings.DOMAIN_NAME}{obj.image.url}"
        else:
            return None
    
    def get_total_count(self, obj):
        classifieds = Classified.objects.filter(category=obj, is_deleted=False, is_active=True).count()
        return classifieds

            
class DetailClassifiedCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassifiedCategory
        fields = ['id', 'title']


class DetailClassifiedSubCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ClassifiedSubCategory
        fields = ['id', 'title']


class DetailClassifiedSubSubCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ClassifiedSubSubCategory
        fields = ['id', 'title']


class PostClassifiedSerializer(serializers.ModelSerializer):
    classified_image = serializers.ListField(
        required=False, 
        allow_null=True,
        child=serializers.FileField(
            max_length=1000000, 
            allow_empty_file=True, 
            use_url=False
        )
    )
    classified_video = serializers.ListField(required=False, allow_null=True,
                                       child=serializers.FileField(
                                           max_length=1000000, allow_empty_file=True, use_url=False
                                       ))
    class Meta:
        model = Classified
        fields = '__all__'
        
    def create(self, validated_data):
        """
        Override the create method to add custom validation
        - Create a post with every classified creation.
        - Validate media formats.
        - Create ClassifiedMedia objects with every media.
        """
        try:
            use = validated_data['profile']
            try:
                user = Profile.objects.get(id=use.id)
            except ObjectDoesNotExist:
                error = serializers.ValidationError({'success': False, 'response': {'message': 'User does not exist'}})
                error.status_code = 404
                raise error
        except:
            error = serializers.ValidationError({'success': False, 'response': {'message': 'Please, Enter User ID'}})
            error.status_code = 400
            raise error
        try:
            classified_images = validated_data.pop('classified_image')
        except:
            classified_images = None
        # Condition to check maximum number of images.
        if classified_images:
            if len(classified_images) > 20:
                error = serializers.ValidationError({'success': False, 'response': {
                    'message': 'You can only upload 20 Images for one Classified'}})
                error.status_code = 400
                raise error
        try:
            classified_videos = validated_data.pop('classified_video')
        except:
            classified_videos = None
        # Condition to check maximum number of videos.
        if classified_videos:
            if len(classified_videos) > 2:
                error = serializers.ValidationError({'success': False, 'response': {
                            'message': 'You can only upload 1 Videos for one Classified'}})
                error.status_code = 400
                raise error
        try:
            privacy = validated_data['privacy']
        except:
            privacy = 'Public'
        def create(self, validated_data):
            classified = Classified.objects.create(**validated_data)
            return classified
        classified = create(self, validated_data)

        post = Post.objects.create(
            profile=user,
            privacy=privacy,
            classified_post=True
        )
        classified.post = post
        classified.save()
        if classified_images is not None:
            for i in classified_images:
                name = i.name.split('.')
                if name[-1].strip() in ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG']:
                    ClassifiedMedia.objects.create(
                        profile=user,
                        post=post,
                        classified=classified,
                        classified_image=i
                    )
                else:
                    raise serializers.ValidationError({'success': False, 'response': {
                                'message': 'Error in classified_image field,'
                                'Only these formats are allowed {}'.format(
                                ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG'])}})
        if classified_videos is not None:
            for classified_video in classified_videos:
                name = classified_video.name.split('.')
                if name[-1] in ['mp4', 'mkv', 'webm', 'avi', 'flv', 'wmv', 'mov', 'MP4', 'MKV', 'WEBM', 'AVI', 'FLV', 'WMV', 'MOV']:
                    if classified_video.size > 75000000:
                        error = serializers.ValidationError({'success': False,'response': {
                                    'message': 'Error in Classified video size. Maximum allowed size is 75mb.'}})
                        error.status_code = 400
                        raise error
                    else:
                        obj = ClassifiedMedia(
                                profile=user,
                                classified=classified,
                                post=post,
                                classified_video=classified_video
                            )
                        obj.save()
                else:
                    raise serializers.ValidationError(
                        {
                            'success': False,
                            'response': {
                            'message': 'Error in classified_video field,' 'Only these formats are allowed {}'.format(
                                                                 ['mp4', 'mkv', 'webm', 'avi', 'flv', 'wmv', 'mov', 'MP4', 'MKV', 'WEBM', 'AVI', 'FLV', 'WMV', 'MOV']
                                                                 )
                            }
                        }
                    )
        return classified


class ClassifiedMediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClassifiedMedia
        fields = ['id', 'classified_image', 'classified_video']


    def to_representation(self, obj):
        return_dict = dict()
        if obj.classified_image:
            return_dict['id'] = obj.id
            return_dict['classified_image'] = f"{settings.S3_BUCKET_LINK}{obj.classified_image}"
        if obj.classified_video:
            return_dict['id'] = obj.id
            return_dict['classified_video'] = f"{settings.S3_BUCKET_LINK}{obj.classified_video}"
            if obj.classified_video_thumbnail:
                return_dict['id'] = obj.id
                return_dict['classified_video_thumbnail'] = f"{settings.S3_BUCKET_LINK}{obj.classified_video_thumbnail}"
            else:
                return_dict['classified_video_thumbnail'] = ''

        return return_dict


class ClassifiedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'text']
class ClassifiedImageMediaSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.classified_image:
            return f"{settings.S3_BUCKET_LINK}{obj.classified_image}"
    class Meta:
        model = ClassifiedMedia
        fields = ['id', 'image']


class ClassifiedVideoMediaSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()
    video_thumbnail = serializers.SerializerMethodField()

    def get_video(self, obj):
        if obj.classified_video:
            return f"{settings.S3_BUCKET_LINK}{obj.classified_video}"

    def get_video_thumbnail(self, obj):
        if obj.classified_video_thumbnail:
            return f"{settings.S3_BUCKET_LINK}{obj.classified_video_thumbnail}"
    class Meta:
        model = ClassifiedMedia
        fields = ['id','video' , 'video_thumbnail']

class ClassifiedGetSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    sub_category = serializers.SerializerMethodField()
    image_media = serializers.SerializerMethodField()
    video_media = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    total_saved = serializers.SerializerMethodField()
    deal_data = serializers.SerializerMethodField()

    def get_deal_data(self, obj):
        try:
            deal_data = DealData.objects.get(classified=obj, is_deleted=False)
            return DealDataSerializer(deal_data).data
        except:
            return None

    def get_total_saved(self, obj):

        favourite = FavouriteClassified.objects.filter(classified=obj, is_deleted=False).count()
        if favourite:
            return favourite
        else:
            return None
    def get_profile(self, classified):
        return DefaultProfileSerializer(classified.profile).data

    def get_company(self, classified):
        if classified.business_type == 'Company':
            try:
                company = Company.objects.get(profile=classified.profile, company_type='Classified')
                return CompanySerializer(company).data
            except:
                return None

    def get_currency(self, classified):
        return CurrencySerializer(classified.currency).data

    def get_category(self, classified):
        return DetailClassifiedCategorySerializer(classified.category).data

    def get_sub_category(self, classified):
        return DetailClassifiedSubCategorySerializer(classified.sub_category).data
    
    def get_brand(self, classified):
        if classified.make:
            return ClassifiedeMakeSerializer(classified.make).data
        else:
            return None

    def get_image_media(self, classified):
        return ClassifiedImageMediaSerializer(classified.classifiedmedia_classified.filter(is_deleted=False).exclude(classified_image=''), many=True).data

    def get_video_media(self, classified):
        return ClassifiedVideoMediaSerializer(classified.classifiedmedia_classified.filter(is_deleted=False).exclude(classified_video=''), many=True).data

    def get_is_favourite(self, obj):
        try:
            profile = self.context.get("profile")
            favourite = FavouriteClassified.objects.get(classified=obj, profile=profile, is_deleted=False)
            return True
        except:
            return False

    class Meta:
        model = Classified
        fields = ['id', 'category', 'sub_category',  'brand', 'is_favourite', 'company',
                  'profile', 'name',  'image_media', 'video_media', 'business_type',
                  'street_adress', 'longitude', 'latitude', 'dial_code', 'mobile',
                  'currency', 'price', 'description', 'type', 'is_active', 'view_count', 'total_saved',
                  'verification_status', 'is_promoted', 'created_at', 'updated_at', 'slug', 'deal_data', 
                  'established_year' , 'employees_count', 'is_deal', 'deal_price' ]


class ClassifiedListingMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassifiedMedia
        fields = ['classified_image', 'classified_video']

    def to_representation(self, obj):
        return_dict = dict()
        if obj.classified_image:
            return_dict['id'] = obj.id
            return_dict['classified_image'] = f"{settings.S3_BUCKET_LINK}{obj.classified_image}"
        if obj.classified_video:
            return_dict['id'] = obj.id
            return_dict['classified_video'] = f"{settings.S3_BUCKET_LINK}{obj.classified_video}"
        return return_dict


class ClassifiedListingSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    sub_category = serializers.SerializerMethodField()
    sub_sub_category = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()

    def get_profile(self, classified):
        return DefaultProfileSerializer(classified.profile, many=False).data

    def get_currency(self, classified):
        return CurrencySerializer(classified.currency).data

    def get_category(self, classified):
        return DetailClassifiedCategorySerializer(classified.category, many=False).data

    def get_sub_category(self, classified):
        return DetailClassifiedSubCategorySerializer(classified.sub_category, many=False).data

    def get_sub_sub_category(self, classified):
        return DetailClassifiedSubSubCategorySerializer(classified.sub_sub_category, many=False).data

    def get_media(self, classified):
        return ClassifiedMediaSerializer(classified.classifiedmedia_classified.filter(is_deleted=False), many=True).data

    def get_country(self, classified):
        return CountrySerializer(classified.country, many=False).data

    def get_state(self, classified):
        return StateSerializer(classified.state, many=False).data

    def get_city(self, classified):
        return CitySerializer(classified.city, many=False).data

    def get_is_favourite(self, obj):
        try:
            profile = self.context.get("profile")
            favourite = FavouriteClassified.objects.get(classified=obj, profile=profile, is_deleted=False)
            return True
        except:
            return False

    class Meta:
        model = Classified
        fields = ['id', 'category', 'sub_category', 'sub_sub_category', 'profile', 'name', 
        'slug', 'country', 'state', 'city', 'street_adress', 'longitude', 'latitude', 'mobile',
        'email', 'type', 'currency', 'price', 'deal_price', 'description', 'quantity', 'is_deal', 
        'media', 'is_favourite', 'created_at', 'is_promoted'
        ]


class ClassifiedFavouriteListingSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    sub_category = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField('check_favorite')

    def get_profile(self, classified):
        return DefaultProfileSerializer(classified.profile, many=False).data

    def get_currency(self, classified):
        return CurrencySerializer(classified.currency, many=False).data

    def get_category(self, classified):
        return DetailClassifiedCategorySerializer(classified.category, many=False).data

    def get_sub_category(self, classified):
        return DetailClassifiedSubCategorySerializer(classified.sub_category, many=False).data

    def get_media(self, classified):
        return ClassifiedMediaSerializer(classified.classifiedmedia_set.filter(is_deleted=False), many=True).data

    def check_favorite(self, obj):
        return True

    class Meta:
        model = Classified
        fields = '__all__'


class ClassifiedFavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavouriteClassified
        fields = '__all__'


class ClassifiedContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactClassified
        fields = '__all__'


class ClassifiedReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportClassified
        fields = '__all__'


class UpdateClassifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classified
        fields = '__all__'