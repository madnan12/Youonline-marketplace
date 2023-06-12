
import profile
from pyexpat import model
from rest_framework import serializers
from youonline_social_app.serializers.post_serializers import DefaultProfileSerializer, PostSerializer
from youonline_social_app.serializers.utility_serializers import LanguageSerializer
from . models import *
from django.conf import settings

# Blog Category Serializer
class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = '__all__'


# Blog Serializer
class BlogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Blog
        fields = '__all__'
    


# Blog Watched Serializer
class BlogWatchedSerializer(serializers.ModelSerializer):
    class Meta: 
        model=BlogWatched
        fields='__all__'


# Get Blog Serializer
class GetBlogSerializer(serializers.ModelSerializer):
    total_comments = serializers.SerializerMethodField()
    featured_image = serializers.SerializerMethodField()
    language = LanguageSerializer(read_only=True)
    rtl = serializers.SerializerMethodField()
    category = BlogCategorySerializer(read_only=True)
    profile = DefaultProfileSerializer(read_only=True)

    class Meta:
        model = Blog
        fields = ['id', 'category', 'profile', 'language', 'post', 'title', 'slug',
                    'description', 'posted_date', 'view_count', 'shared_count',
                    'is_promoted', 'is_deleted', 'created_at',
                    'updated_at', 'is_compressed', 'featured_image', 'total_comments', 'rtl']

    def get_featured_image(self, obj):
        request = self.context.get('request')
        try:
            blog_media = BlogMedia.objects.get(blog=obj)
            if blog_media.featured_image:
                return f"{settings.S3_BUCKET_LINK}{blog_media.featured_image}"
            else:
                return None
        except Exception as e:
            print(e)
            return None
        

    def get_total_comments(self, obj):
        request=self.context.get('request')
        if obj.post:
            total_comment=obj.post.comments_count
            return total_comment
        else:
            None

    def get_rtl(self, obj):

        try:
            rtl = Language.objects.get(id=obj.language.id)
            if rtl.rtl == True:
                rtl=True
            else:
                rtl=False
            return rtl
        except Exception as e:
            pass
        
class BlogAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogAuthor
        fields = '__all__'
        
class GetBlogAuthorSerializer(serializers.ModelSerializer):
    profile = DefaultProfileSerializer(read_only=True)
    resume =serializers.SerializerMethodField()

    def get_resume(self, obj):
        if obj.resume:
            resume_url = obj.resume
            print(f"{settings.S3_BUCKET_LINK}{resume_url}")
            return f"{settings.S3_BUCKET_LINK}{resume_url}"
        else:
            return None
    class Meta:
        model = BlogAuthor
        fields = ['id', 'profile', 'first_name', 'last_name', 'description', 'resume' , 'language', 'country', 'is_deleted', 'created_at', 'updated_at']