
from . models import *
from youonline_social_app.models import *
from community_app.serializers import DefaultPageSerializer
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
from youonline_social_app.serializers import users_serializers
from youonline_social_app.serializers import post_serializers


# Group Serializers
class BusinessOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessOwner
        fields = '__all__'


class GetBusinessOwnerSerializer(serializers.ModelSerializer):
    profile = users_serializers.DefaultProfileSerializer(read_only=True)
    profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = BusinessOwner
        fields = '__all__'

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            return f"{settings.S3_BUCKET_LINK}{obj.profile_picture}"
        else:
            return None


class BusinessDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessDetails
        fields = '__all__'


class GetBusinessDetailsSerializer(serializers.ModelSerializer):
    owner = GetBusinessOwnerSerializer(read_only=True)
    page = DefaultPageSerializer(read_only=True)
    class Meta:
        model = BusinessDetails
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
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
        model = Product
        fields = '__all__'

    def create(self, validated_data):
        """
        Overridding of the default create method in a Serializer
        Some of the main functions/validations are as follows:
        - Create Post
        - Create Product
        - Create Product Media
        """
        # Validate Product Media
        try:
            images = validated_data.pop('images')
        except:
            images = None
        try:
            videos = validated_data.pop('videos')
        except:
            videos = None
        if images == None and videos == None:
            error = serializers.ValidationError(
                {'success': False, 'response': {'message': 'Please enter media.'}})
            error.status_code = 400
            raise error
        
        # Validate User.
        try:
            profile = self.context['profile']
            try:
                user = Profile.objects.get(id=profile)
            except ObjectDoesNotExist:
                error = serializers.ValidationError(
                    {'success': False, 'response': {'message': 'User does not exist'}})
                error.status_code = 404
                raise error
        except Exception as e:
            error = serializers.ValidationError(
                {'success': False, 'response': {'message': str(e)}})
            error.status_code = 400
            raise error

        # Valdiate Product details
        try:
            business_details = validated_data.pop('business_details')
        except:
            error = serializers.ValidationError(
                {
                    'success': False, 
                    'response': {
                        'message': 
                        'Business Details is required.'
                    }
                }
            )
            error.status_code = 400
            raise error
        try:
            title = validated_data.pop('title')
        except:
            error = serializers.ValidationError(
                {
                    'success': False, 
                    'response': {
                        'message': 
                        'Title is required.'
                    }
                }
            )
            error.status_code = 400
            raise error
        try:
            description = validated_data.pop('description')
        except:
            error = serializers.ValidationError(
                {
                    'success': False, 
                    'response': {
                        'message': 
                        'Description is required.'
                    }
                }
            )
            error.status_code = 400
            raise error
        try:
            category = validated_data.pop('category')
        except:
            error = serializers.ValidationError(
                {
                    'success': False, 
                    'response': {
                        'message': 
                        'Category is required.'
                    }
                }
            )
            error.status_code = 400
            raise error
        try:
            subcategory = validated_data.pop('subcategory')
        except:
            subcategory = None
        try:
            brand = validated_data.pop('brand')
        except:
            error = serializers.ValidationError(
                {
                    'success': False, 
                    'response': {
                        'message': 
                        'Brand is required.'
                    }
                }
            )
            error.status_code = 400
            raise error
        try:
            color = validated_data.pop('color')
        except:
            color = ""
        try:
            size = validated_data.pop('size')
        except:
            size = ""
        try:
            condition = validated_data.pop('condition')
        except:
            condition = ""
        try:
            material = validated_data.pop('material')
        except:
            material = ""
        try:
            quantity = validated_data.pop('quantity')
        except:
            error = serializers.ValidationError(
                {
                    'success': False, 
                    'response': {
                        'message': 
                        "Quantity is required."
                    }
                }
            )
            error.status_code = 400
            raise error
        try:
            cost_price = validated_data.pop('cost_price')
        except:
            error = serializers.ValidationError(
                {
                    'success': False, 
                    'response': {
                        'message': 
                        'Cost Price is required.'
                    }
                }
            )
            error.status_code = 400
            raise error
        try:
            sale_price = validated_data.pop('sale_price')
        except:
            error = serializers.ValidationError(
                {
                    'success': False, 
                    'response': {
                        'message': 
                        "Sale price is required."
                    }
                }
            )
            error.status_code = 400
            raise error
        try:
            publish_status = validated_data.pop('publish_status')
        except:
            publish_status = "Published"
        
        # create Post with the basic details
        post = Post.objects.create(
            profile=user,
            text=title,
            normal_post=False,
            product_post=True,
        )
        # create Product with the basic details
        product = Product(
            post=post,
            business_details=business_details,
            title=title,
            description=description,
            category=category,
            subcategory=subcategory,
            brand=brand,
            color=color,
            size=size,
            condition=condition,
            material=material,
            quantity=quantity,
            cost_price=cost_price,
            sale_price=sale_price,
            publish_status=publish_status,
        )
        product.save(commit=False)

        if product.publish_status == 'Scheduled':
            try:
                schedule_time = self.context['schedule_time']
            except:
                schedule_time = None
            if not schedule_time:
                error = serializers.ValidationError(
                    {'success': False, 'response': {'message': 'Please enter schedule time.'}})
                error.status_code = 400
                raise error
            ProductSchedule.objects.create(
                product=product,
                profile=user,
                publish_time=schedule_time,
            )

        # Create Product Media
        if images is not None:
            for i in images:
                name = i.name.split('.')
                if name[-1].strip() in ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG']:
                    product_media = ProductMedia(
                        product=product,
                        image=i,
                    )
                    product_media.save()
                else:
                    raise serializers.ValidationError({'success': False,
                                                         'response': {
                                                             'message': 'Error in image field,'
                                                                        'Only these formats are allowed {}'.format(
                                                                 ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG'])}})
        if videos is not None:
            for i in videos:
                try:
                    name = i.name.split('.')
                    if name[-1].strip() in ['mp4', 'mkv', 'webm', 'avi', 'flv', 'wmv', 'mov', 'MP4', 'MKV', 'WEBM', 'AVI', 'FLV', 'WMV', 'MOV']:
                        product_media = ProductMedia(
                            product=product,
                            video=i,
                        )
                        product_media.save()
                    else:
                        raise serializers.ValidationError({'success': False,
                                                             'response': {
                                                                 'message': 'Error in video field,'
                                                                            'Only these formats are allowed {}'.format(
                                                                     ['mp4', 'mkv', 'webm', 'avi', 'flv', 'wmv', 'mov', 'MP4', 'MKV', 'WEBM', 'AVI', 'FLV', 'WMV', 'MOV'])}})
                except Exception as e:
                    print(e)
        product.save()
        return product

    def update(self, product, validated_data):
        """
        Overridding of the default update method in a Serializer
        Some of the main functions/validations are as follows:
        - Update Product
        - Create Product Media
        """
        # Validate Product Media
        try:
            image = validated_data.pop('images')
        except:
            image = None
        try:
            video = validated_data.pop('videos')
        except:
            video = None
        # Get User object
        try:
            profile = self.context['profile']
            try:
                user = Profile.objects.get(id=profile)
            except ObjectDoesNotExist:
                error = serializers.ValidationError(
                    {'success': False, 'response': {'message': 'User does not exist'}})
                error.status_code = 404
                raise error
        except Exception as e:
            error = serializers.ValidationError(
                {'success': False, 'response': {'message': str(e)}})
            error.status_code = 400
            raise error

        # Valdiate Product details
        try:
            title = validated_data.pop('title')
        except:
            title = None
        try:
            description = validated_data.pop('description')
        except:
            description = None
        try:
            category = validated_data.pop('category')
        except:
            category = None
        try:
            subcategory = validated_data.pop('subcategory')
        except:
            subcategory = None
        try:
            brand = validated_data.pop('brand')
        except:
            brand = None
        try:
            color = validated_data.pop('color')
        except:
            color = None
        try:
            size = validated_data.pop('size')
        except:
            size = None
        try:
            condition = validated_data.pop('condition')
        except:
            condition = None
        try:
            material = validated_data.pop('material')
        except:
            material = None
        try:
            quantity = validated_data.pop('quantity')
        except:
            quantity = None
        try:
            cost_price = validated_data.pop('cost_price')
        except:
            cost_price = None
        try:
            sale_price = validated_data.pop('sale_price')
        except:
            sale_price = None
        try:
            publish_status = validated_data.pop('publish_status')
        except:
            publish_status = None

        if title is not None and title != "":
            product.title = title
        if description is not None and description != "":
            product.description = description
        if category is not None and category != "":
            product.category = category
        if subcategory is not None and subcategory != "":
            product.subcategory = subcategory
        if brand is not None and brand != "":
            product.brand = brand
        if color is not None and color != "":
            product.color = color
        if size is not None and size != "":
            product.size = size
        if condition is not None and condition != "":
            product.condition = condition
        if material is not None and material != "":
            product.material = material
        if quantity is not None and quantity != "":
            product.quantity = quantity
        if cost_price is not None and cost_price != "":
            product.cost_price = cost_price
        if sale_price is not None and sale_price != "":
            product.sale_price = sale_price
        if publish_status is not None and publish_status != "":
            product.publish_status = publish_status
        if product.publish_status == 'Scheduled':
            try:
                schedule_time = self.context['schedule_time']
            except:
                schedule_time = None
            if not schedule_time:
                error = serializers.ValidationError(
                    {'success': False, 'response': {'message': 'Please enter schedule time.'}})
                error.status_code = 400
                raise error
            try:
                product_schedule = ProductSchedule.objects.get(product=product)
                product_schedule.publish_time = schedule_time
                product_schedule.save()
            except:
                ProductSchedule.objects.create(
                    product=product,
                    profile=user,
                    publish_time=schedule_time,
                )
        product.save()

        # Create Product Media
        if image is not None:
            for i in image:
                name = i.name.split('.')
                if name[-1].strip() in ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG']:
                    product_media = ProductMedia(
                        product=product,
                        image=i,
                    )
                    product_media.save()
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
                        product_media = ProductMedia(
                            product=product,
                            video=i,
                        )
                    else:
                        raise serializers.ValidationError({'success': False,
                                                             'response': {
                                                                 'message': 'Error in video field,'
                                                                            'Only these formats are allowed {}'.format(
                                                                     ['mp4', 'mkv', 'webm', 'avi', 'flv', 'wmv', 'mov', 'MP4', 'MKV', 'WEBM', 'AVI', 'FLV', 'WMV', 'MOV'])}})
                except Exception as e:
                    print(e)
        return product


class GetProductMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMedia
        fields = '__all__'


    def to_representation(self, instance):
        if instance.image:
            image = f"{settings.S3_BUCKET_LINK}{instance.image}"
        else:
            image = None
        if instance.image_thumbnail:
            image_thumbnail = f"{settings.S3_BUCKET_LINK}{instance.image_thumbnail}"
        else:
            image_thumbnail = None
        if instance.video:
            video = f"{settings.S3_BUCKET_LINK}{instance.video}"
        else:
            video = None
        if instance.video_thumbnail:
            video_thumbnail = f"{settings.S3_BUCKET_LINK}{instance.video_thumbnail}"
        else:
            video_thumbnail = None
        return {
            'id': instance.id,
            'image': image,
            'image_thumbnail': image_thumbnail,
            'video': video,
            'video_thumbnail': video_thumbnail,
        }


class GetProductSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'business_details', 'post', 'title',
                  'description', 'category', 'subcategory',
                  'brand', 'url', 'color', 'size', 'condition',
                  'material', 'status', 'quantity', 'availability',
                  'is_deleted', 'cost_price', 'sale_price',
                  'created_at', 'updated_at', 'publish_status', 'media']

    
    def get_media(self, obj):
        serializer = GetProductMediaSerializer(obj.productmedia_product.all(), many=True)
        return serializer.data


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSubCategory
        fields = '__all__'

class ArchivedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivedProduct
        fields = '__all__'

class GetArchivedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivedProduct
        fields = '__all__'


class CollectionProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionProduct
        fields = ['owner', 'title', 'description']

class GetCollectionProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True, many=True)
    class Meta:
        model = CollectionProduct
        fields = '__all__'