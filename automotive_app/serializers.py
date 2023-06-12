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
from classified_app.serializers import *
from property_app.serializers import *
from job_app.serializers import *


class AutomotiveMakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomotiveMake
        fields = '__all__'

#  Sub Sub Category Automotive Serializer
class AutomotiveSubSubCategorySerializer(serializers.ModelSerializer):
    total_count = serializers.SerializerMethodField()

    def get_total_count(self, obj):
        automotive = Automotive.objects.filter(sub_sub_category=obj, is_deleted=False, is_active=True).count()
        return automotive
    class Meta:
        model = AutomotiveSubSubCategory
        fields = ['id', 'title', 'total_count']


#  Sub Category Automotive Serializer
class AutomotiveSubCategorySerializer(serializers.ModelSerializer):
    sub_sub_category = serializers.SerializerMethodField()
    total_count = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            return f"{settings.DOMAIN_NAME}{obj.image.url}"
        else:
            return None

    def get_sub_sub_category(self, obj):
        sub_sub_category = AutomotiveSubSubCategory.objects.filter(sub_category=obj)
        return AutomotiveSubSubCategorySerializer(sub_sub_category, many=True).data

    def get_total_count(self, obj):
        automotive = Automotive.objects.filter(sub_category=obj, is_deleted=False, is_active=True).count()
        return automotive
    class Meta:
        model = AutomotiveSubCategory
        fields = ['id', 'title', 'sub_sub_category', 'image', 'background_color', 'total_count']


#  Category Automotive Serializer
class AutomotiveCategorySerializer(serializers.ModelSerializer):
    sub_category = serializers.SerializerMethodField()
    total_count = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_sub_category(self, obj):
        sub_category = AutomotiveSubCategory.objects.filter(category=obj)
        return AutomotiveSubCategorySerializer(sub_category, many=True).data

    def get_image(self, obj):
        if obj.image:
            return f"{settings.DOMAIN_NAME}{obj.image.url}"
        else:
            return None

    def get_total_count(self, obj):
        automotives = Automotive.objects.filter(category=obj, is_deleted=False, is_active=True).count()
        return automotives
    class Meta:
        model = AutomotiveCategory
        fields = ['id', 'title', 'sub_category', 'image', 'background_color', 'total_count']

class AutomotiveGetMakeAndModelSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self,obj):
        if obj.image:
            return f'{settings.DOMAIN_NAME}{obj.image.url}'
    

    class Meta:
        model = AutomotiveMake
        fields = ['id', 'title', 'image']

# Detail Category Automotive Serializer
class DetailCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            return f"{settings.DOMAIN_NAME}{obj.image.url}"
        else:
            return None
    class Meta:
        model = AutomotiveCategory
        fields = ['id', 'title', 'image', 'background_color']


# Detail Sub Category Automotive Serializer
class DetailSubCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            return f"{settings.DOMAIN_NAME}{obj.image.url}"
        else:
            return None

    class Meta:
        model = AutomotiveSubCategory
        fields = ['id', 'title', 'image', 'background_color']


# Detail Sub Sub Category Automotive Serializer
class DetailSubSubCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            return f"{settings.DOMAIN_NAME}{obj.image.url}"
        else:
            return None
            
    class Meta:
        model = AutomotiveSubSubCategory
        fields = ['id', 'title', 'image', 'background_color']


#  Automotive Serializer
class AutomotiveSerializer(serializers.ModelSerializer):
    automotive_image = serializers.ListField(required=False, allow_null=True,
                                       child=serializers.FileField(
                                           max_length=1000000, allow_empty_file=True, use_url=False
                                       ))
    automotive_videos = serializers.ListField(required=False, allow_null=True,
                                       child=serializers.FileField(
                                           max_length=1000000, allow_empty_file=True, use_url=False
                                       ))

    class Meta:
        model = Automotive
        fields = '__all__'

    def create(self, validated_data):
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
            automotive_images = validated_data.pop('automotive_image')
        except:
            automotive_images = None
        # Condition to check maximum number of images.
        if automotive_images:
            if len(automotive_images) > 10:
                error = serializers.ValidationError({'success': False,
                                                     'response': {
                                                         'message': 'You can only upload 10 images for one Automotive'}})
                error.status_code = 400
                raise error
        try:
            automotive_videos = validated_data.pop('automotive_videos')
        except:
            automotive_videos = None
        # Condition to check maximum number of videos.
        if automotive_videos:
            if len(automotive_videos) > 2:
                error = serializers.ValidationError({'success': False,
                                                     'response': {
                                                         'message': 'You can only upload 2 Videos for one Automotive'}})
                error.status_code = 400
                raise error
        try:
            privacy = validated_data['privacy']
        except:
            privacy = 'Public'

        automotive = Automotive.objects.create(**validated_data)
        post = Post.objects.create(
            profile=user,
            privacy=privacy,
            automotive_post=True
        )
        automotive.post = post
        automotive.save()
        if automotive_images is not None:
            for i in automotive_images:
                name = i.name.split('.')
                if name[-1].strip() in ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG']:
                    automedia = AutomotiveMedia.objects.create(
                        profile=user,
                        post=post,
                        automotive=automotive,
                        automotive_image=i
                    )
                    automedia.save()
                else:
                     raise serializers.ValidationError({'success': False,
                                                         'response': {
                                                             'message': 'Error in automotive Image field,'
                                                                        'Only these formats are allowed {}'.format(
                                                                 ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG'])}})
        if automotive_videos is not None:
            for i in automotive_videos:
                name = i.name.split('.')
                if name[-1].strip() in ['mp4', 'mkv', 'webm', 'avi', 'flv', 'wmv', 'mov', 'MP4', 'MKV', 'WEBM', 'AVI', 'FLV', 'WMV', 'MOV']:
                    automedia = AutomotiveMedia.objects.create(
                        profile=user,
                        post=post,
                        automotive=automotive,
                        automotive_video=i
                    )
                    automedia.save()
                else:
                     raise serializers.ValidationError({'success': False,
                                                         'response': {
                                                             'message': 'Error in automotive Video field,'
                                                                        'Only these formats are allowed {}'.format(
                                                                 ['mp4', 'mkv', 'webm', 'avi', 'flv', 'wmv', 'mov', 'MP4', 'MKV', 'WEBM', 'AVI', 'FLV', 'WMV', 'MOV'])}})
        return automotive


#  Automotive Media Serializer
class AutomotiveMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomotiveMedia
        fields = ['automotive_image', 'automotive_video', 'vid_thumbnail']

    def to_representation(self, obj):
        return_dict = dict()
        if obj.vid_thumbnail:
            return_dict['id'] = obj.id
            return_dict['automotive'] = obj.automotive.id
            return_dict['vid_thumbnail'] = f"{settings.S3_BUCKET_LINK}{obj.vid_thumbnail}"
        if obj.automotive_image:
            return_dict['id'] = obj.id
            return_dict['automotive'] = obj.automotive.id
            return_dict['automotive_image'] = f"{settings.S3_BUCKET_LINK}{obj.automotive_image}"
        if obj.automotive_video:
            return_dict['id'] = obj.id
            return_dict['automotive'] = obj.automotive.id
            return_dict['automotive_video'] = f"{settings.S3_BUCKET_LINK}{obj.automotive_video}"
        return_dict["name"] = obj.automotive.name
        return return_dict


# Automotive Post Serializer
class AutomotivePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'text']


class AutomotiveImageMediaSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.automotive_image:
            return f"{settings.S3_BUCKET_LINK}{obj.automotive_image}"
    class Meta:
        model = AutomotiveMedia
        fields = ['id', 'image']


class AutomotiveVideoMediaSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()
    video_thumbnail = serializers.SerializerMethodField()

    def get_video(self, obj):
        if obj.automotive_video:
            return f"{settings.S3_BUCKET_LINK}{obj.automotive_video}"

    def get_video_thumbnail(self, obj):
        if obj.vid_thumbnail:
            return f"{settings.S3_BUCKET_LINK}{obj.vid_thumbnail}"
    class Meta:
        model = AutomotiveMedia
        fields = ['id','video' , 'video_thumbnail']



# Get Automotive Serializer 
class GetAutomotiveSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()

    currency = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    sub_category = serializers.SerializerMethodField()
    image_media = serializers.SerializerMethodField()
    video_media = serializers.SerializerMethodField()
    make = serializers.SerializerMethodField()
    automotive_model = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()
    total_saved = serializers.SerializerMethodField()
    deal_data = serializers.SerializerMethodField()

    def get_deal_data(self, automotive):
        try:
            deal_data = DealData.objects.get(automotive=automotive, is_deleted=False)
            return DealDataSerializer(deal_data).data
        except:
            return None

    def get_profile(self, automotive):
        return DefaultProfileSerializer(automotive.profile, many=False).data
    
    def get_company(self, automotive):
        if automotive.business_type == 'Company':
            try:
                company = Company.objects.get(profile=automotive.profile, company_type='Automotive')
                return CompanySerializer(company).data
            except:
                return None

    def get_currency(self, automotive):
        return CurrencySerializer(automotive.currency, many=False).data


    def get_category(self, automotive):
        return DetailCategorySerializer(automotive.category, many=False).data

    def get_sub_category(self, automotive):
        return DetailSubCategorySerializer(automotive.sub_category, many=False).data
   
    def get_image_media(self, automotive):
        return AutomotiveImageMediaSerializer(automotive.automotivemedia_automotive.filter(is_deleted=False).exclude(automotive_image=''), many=True).data

    def get_video_media(self, automotive):
        return AutomotiveVideoMediaSerializer(automotive.automotivemedia_automotive.filter(is_deleted=False).exclude(automotive_video=''), many=True).data

    def get_is_favourite(self, obj):
        try:
            profile = self.context.get("profile")
            favourite = FavouriteAutomotive.objects.get(automotive=obj, profile=profile, is_deleted=False)
            return True
        except:
            return False
    
    def get_total_saved(self, obj):

        favourite = FavouriteAutomotive.objects.filter(automotive=obj, is_deleted=False).count()
        if favourite:
            return favourite
        else:
            return None

    # def get_deal(self, automotive):
    #     try:
    #         deal_data = DealData.objects.get(automotive=automotive, is_deleted=False, is_expired=False, deal_automotive=True)[-1]
    #         return DealDataSerializer(deal_data, many=False).data
    #     except:
    #         return None

    def get_make(self, automotive):
        if automotive.make:
            return AutomotiveGetMakeAndModelSerializer(automotive.make).data
        else:
            return None

    def get_automotive_model(self, automotive):
        return GetAutomotiveModelSerializer(automotive.automotive_model).data

    class Meta:
        model = Automotive
        fields = ['id', 'name', 'currency','is_favourite', 'company',
                  'category', 'sub_category','price', 'dial_code',
                  'profile', 'image_media', 'video_media', 'mobile','business_type', 
                 'street_adress', 'longitude', 'latitude', 'make', 'automotive_model',
                  'description', 'car_type', 'quantity', 'kilometers', 'automotive_year', 'total_saved',
                   'transmission_type', 'slug', 'is_deal', 'deal_data', 'is_promoted', 'is_active', 'view_count',
                  'fuel_type', 'verification_status', 'updated_at', 'created_at'
                  ]


# Automotive Listing Media Serializer 
class AutomotiveListingMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomotiveMedia
        fields = ['automotive_image', 'automotive_video']

    def to_representation(self, obj):
        return_dict = dict()
        if obj.automotive_image:
            return_dict['id'] = obj.id
            return_dict['automotive'] = obj.automotive.id
            return_dict['automotive_image'] = f"{settings.S3_BUCKET_LINK}{obj.automotive_image}"
        if obj.automotive_video:
            return_dict['id'] = obj.id
            return_dict['automotive'] = obj.automotive.id
            return_dict['automotive_video'] = f"{settings.S3_BUCKET_LINK}{obj.automotive_video}"
            return_dict['vid_thumbnail'] = f"{settings.S3_BUCKET_LINK}{obj.vid_thumbnail}"
        return return_dict


# Automotive Listing Serializer
class AutomotiveListingSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    sub_category = serializers.SerializerMethodField()
    sub_sub_category = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()

    def get_profile(self, automotive):
        return DefaultProfileSerializer(automotive.profile, many=False).data

    def get_currency(self, automotive):
        return CurrencySerializer(automotive.currency, many=False).data

    def get_country(self, automotive):
        return CountrySerializer(automotive.country, many=False).data

    def get_state(self, automotive):
        return StateSerializer(automotive.state, many=False).data

    def get_city(self, automotive):
        return CitySerializer(automotive.city, many=False).data

    def get_category(self, automotive):
        return DetailCategorySerializer(automotive.category, many=False).data

    def get_sub_category(self, automotive):
        return DetailSubCategorySerializer(automotive.sub_category, many=False).data

    def get_sub_sub_category(self, automotive):
        return DetailSubSubCategorySerializer(automotive.sub_sub_category, many=False).data

    def get_media(self, automotive):
        return AutomotiveListingMediaSerializer(automotive.automotivemedia_automotive.filter(is_deleted=False), many=True).data

    def get_is_favourite(self, obj):
        try:
            profile = self.context.get("profile")
            favourite = FavouriteAutomotive.objects.get(automotive=obj, profile=profile, is_deleted=False)
            return True
        except:
            return False

    class Meta:
        model = Automotive
        fields = ['id', 'slug', 'name', 'currency', 'country', 'state', 'city', 'is_favourite',
                  'category', 'sub_category', 'sub_sub_category', 'price', 'car_type',
                  'profile', 'media', 'created_at']


# Automotive Favourite Listing Serializer
class AutomotiveFavouriteListingSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    sub_category = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()

    def get_is_favourite(self, automotive):
        return True
        
    def get_profile(self, automotive):
        return DefaultProfileSerializer(automotive.profile, many=False).data

    def get_currency(self, automotive):
        return CurrencySerializer(automotive.currency, many=False).data

    def get_category(self, automotive):
        return DetailCategorySerializer(automotive.category, many=False).data

    def get_sub_category(self, automotive):
        return DetailSubCategorySerializer(automotive.sub_category, many=False).data

    def get_media(self, automotive):
        return AutomotiveListingMediaSerializer(automotive.automotivemedia_automotive.all(), many=True).data

    class Meta:
        model = Automotive
        fields = ['id', 'name', 'currency', 'is_favourite',
                  'category', 'sub_category', 'price',
                  'profile', 'media', 'created_at', 'slug']


# Automotive Favourite Serializer
class AutomotiveFavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavouriteAutomotive
        fields = '__all__'


# Automotive Contact Serializer
class AutomotiveContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactAutomotive
        fields = '__all__'


# Automotive Report Serializer
class AutomotiveReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportAutomotive
        fields = '__all__'


# Get Automotive Model Serializer
class GetAutomotiveModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomotiveModel
        fields = '__all__'


# Get Automotive Make Serializer
class GetAutomotiveMakeAndModelSerializer(serializers.ModelSerializer):
    atuomotivemodel_automotivemake = GetAutomotiveModelSerializer(many=True)
    image = serializers.SerializerMethodField()


    def get_image(self,obj):
        if obj.image:
            return f'{settings.DOMAIN_NAME}{obj.image.url}'
    

    class Meta:
        model = AutomotiveMake
        fields = ['id', 'title', 'image', 'atuomotivemodel_automotivemake']



class AutomotiveMakeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    def get_image(self, obj):
        if obj.image:

            return f"{settings.DOMAIN_NAME}{obj.image.url}"
        else:
            return None

    class Meta:
        model = AutomotiveMake
        fields = '__all__'

# Get Automotive Comparision Serializer
class GetAutomotiveComparisonSerializer(serializers.ModelSerializer):
    automotive1 = serializers.SerializerMethodField()
    automotive2 = serializers.SerializerMethodField()


    class Meta:
        model = AutomotiveComparison
        fields = ['automotive1', 'automotive2']


    def get_automotive1(self, obj):
        return GetAutomotiveSerializer(obj.automotive1).data


    def get_automotive2(self, obj):
        return GetAutomotiveSerializer(obj.automotive2).data


# Get Used Car Serializer
class GetUsedCarsSerializer(serializers.ModelSerializer):
    automotive_image = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    make = serializers.SerializerMethodField()
    automotive_model = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    class Meta:
        model = AutomotiveMedia
        fields = ['automotive_image', 'name', 'make', 'automotive_model', 'slug']


    def get_automotive_image(self, obj):
        return_dict = dict()
        if obj.automotive_image:
            return_dict['id'] = obj.id
            return_dict['automotive'] = obj.automotive.id
            return_dict['automotive_image'] = f"{settings.S3_BUCKET_LINK}{obj.automotive_image}"
        return return_dict

    def get_name(self, obj):
        return obj.automotive.name

    def get_make(self, obj):
        return obj.automotive.make.title

    def get_automotive_model(self, obj):
        return obj.automotive.automotive_model.title

    def get_slug(self, obj):
        return obj.automotive.slug


class AutomotiveSearchSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    sub_category = serializers.SerializerMethodField()
    sub_sub_category = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()

    total_min_year_product = serializers.SerializerMethodField()
    total_max_year_product = serializers.SerializerMethodField()
    total_min_price_product = serializers.SerializerMethodField()
    total_max_price_product = serializers.SerializerMethodField()
    total_min_km_product = serializers.SerializerMethodField()
    total_max_km_product = serializers.SerializerMethodField()
    total_brand_product = serializers.SerializerMethodField()
    total_inspection_product = serializers.SerializerMethodField()
    total_fuel_product = serializers.SerializerMethodField()
    total_transmission_product = serializers.SerializerMethodField()

    def get_total_min_year_product(self, automotive):
        min_year = self.context.get("min_year")
        if min_year:
            automotive = Automotive.objects.filter(automotive_year__gte=min_year, is_deleted=False, is_active=True).count()
            return automotive
    
    def get_total_max_year_product(self, automotive):
        max_year = self.context.get("max_year")
        if max_year:
            automotive = Automotive.objects.filter(automotive_year__lte=max_year, is_deleted=False, is_active=True).count()
            return automotive

    def get_total_min_price_product(self, automotive):
        min_price = self.context.get("min_price")
        if min_price:
            automotive = Automotive.objects.filter(price__gte=min_price, is_deleted=False, is_active=True).count()
            return automotive

    def get_total_max_price_product(self, automotive):
        max_price = self.context.get("max_price")
        if max_price:
            automotive = Automotive.objects.filter(price__lte=max_price, is_deleted=False, is_active=True).count()
            return automotive

    def get_total_min_km_product(self, automotive):
        min_km = self.context.get("min_km")
        if min_km:
            automotive = Automotive.objects.filter(kilometers__gte=min_km, is_deleted=False, is_active=True).count()
            return automotive

    def get_total_max_km_product(self, automotive):
        max_km = self.context.get("max_km")
        if max_km:
            automotive = Automotive.objects.filter(kilometers__lte=max_km, is_deleted=False, is_active=True).count()
            return automotive
    
    def get_total_brand_product(self, automotive):
        brand = self.context.get("brand")
        try:
            brand = AutomotiveMake.objects.get(id=brand)
            automotive = Automotive.objects.filter(make__title__icontains=brand, is_deleted=False, is_active=True).count()
            return automotive
        except Exception as e:
            return None

    def get_total_inspection_product(self, automotive):
        automotive_inspection = self.context.get("automotive_inspection")
        if automotive_inspection:
            automotive = Automotive.objects.filter(automotive_inspection__icontains=automotive_inspection, is_deleted=False, is_active=True).count()
            return automotive

    def get_total_transmission_product(self, automotive):
        transmission_type = self.context.get("transmission_type")
        if transmission_type:
            automotive = Automotive.objects.filter(transmission_type__icontains=transmission_type, is_deleted=False, is_active=True).count()
            return automotive

    def get_total_fuel_product(self, automotive):
        fuel_type = self.context.get("fuel_type")
        if fuel_type:
            automotive = Automotive.objects.filter(fuel_type__icontains=fuel_type, is_deleted=False, is_active=True).count()
            return automotive

    def get_profile(self, automotive):
        return DefaultProfileSerializer(automotive.profile, many=False).data

    def get_currency(self, automotive):
        return CurrencySerializer(automotive.currency, many=False).data

    def get_country(self, automotive):
        return CountrySerializer(automotive.country, many=False).data

    def get_state(self, automotive):
        return StateSerializer(automotive.state, many=False).data

    def get_city(self, automotive):
        return CitySerializer(automotive.city, many=False).data

    def get_category(self, automotive):
        return DetailCategorySerializer(automotive.category, many=False).data

    def get_sub_category(self, automotive):
        return DetailSubCategorySerializer(automotive.sub_category, many=False).data

    def get_sub_sub_category(self, automotive):
        return DetailSubSubCategorySerializer(automotive.sub_sub_category, many=False).data

    def get_media(self, automotive):
        return AutomotiveListingMediaSerializer(automotive.automotivemedia_automotive.filter(is_deleted=False), many=True).data

    def get_is_favourite(self, obj):
        try:
            profile = self.context.get("profile")
            favourite = FavouriteAutomotive.objects.get(automotive=obj, profile=profile, is_deleted=False)
            return True
        except:
            return False
    


    class Meta:
        model = Automotive
        fields = [
                'id', 'slug', 'name', 'currency', 'country', 'state', 'city', 'is_favourite',
                'category', 'sub_category', 'sub_sub_category', 'price', 'car_type', 'make',
                'kilometers', 'transmission_type', 'fuel_type', 'automotive_inspection','automotive_year',
                'profile', 'media', 'created_at', 'total_min_year_product', 'total_max_year_product', 
                'total_min_price_product', 'total_max_price_product', 'total_min_km_product', 
                'total_max_km_product', 'total_brand_product', 'total_inspection_product', 'total_fuel_product', 
                'total_transmission_product'
                  ]

class ModuleViewHistorySerializer(serializers.ModelSerializer):
    automotive = serializers.SerializerMethodField()
    property = serializers.SerializerMethodField()
    job = serializers.SerializerMethodField()
    classified = serializers.SerializerMethodField()

    def get_automotive(self, obj):
        if obj.automotive:
            try:
                automotive = Automotive.objects.get(id=obj.automotive.id, is_deleted=False, is_active=True)
                return GetAutomotiveSerializer(automotive).data
            except:
                return None

    def get_property(self, obj):
        if obj.property:
            try:
                property = Property.objects.get(id=obj.property.id, is_deleted=False, is_active=True)
                return PropertyGetSerializer(property).data
            except:
                return None

    def get_job(self, obj):
        if obj.job:
            try:
                job = Job.objects.get(id=obj.job.id, is_deleted=False, is_active=True)
                return GetJobSerializer(job).data
            except:
                return None

    def get_classified(self, obj):
        if obj.classified:
            try:
                classified = Classified.objects.get(id=obj.classified.id, is_deleted=False, is_active=True)
                return ClassifiedGetSerializer(classified).data
            except:
                return None
    class Meta:
        model = ModuleViewHistory
        fields = ['id',  'profile', 'automotive', 'property', 'job', 'classified', 'created_at']