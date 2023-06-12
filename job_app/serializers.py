
from rest_framework import serializers
from youonline_social_app.serializers.post_serializers import DefaultProfileSerializer
from youonline_social_app.serializers.users_serializers import UserHighSchoolSerializer, UserWorkPlaceSerializer, CompanySerializer
from youonline_social_app.serializers.utility_serializers import CountrySerializer, StateSerializer, CitySerializer, LanguageSerializer
from django.core.exceptions import ObjectDoesNotExist
from . models import *
from youonline_social_app.models import *
from django.conf import settings
import os.path


# Jobs Module
# Industry Serializer
class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = '__all__'


# Company Serialzer
class CompanySerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    cover_picture = serializers.SerializerMethodField()

    def get_profile_picture(self, obj):
        try:
            profile_picture = CompanyLogo.objects.get(company=obj.id, is_deleted=False)
            return f"{settings.S3_BUCKET_LINK}{profile_picture.logo}"
        except:
            profile_picture = None
        return profile_picture
    

    def get_cover_picture(self, obj):
        try:
            cover_picture = CompanyCoverImage.objects.get(company=obj, is_deleted=False)
            return f"{settings.S3_BUCKET_LINK}{cover_picture.cover_image}"
        except Exception as e:
            print(e)
            cover_picture = None
        return cover_picture
    class Meta:
        model = Company
        fields = [
                    'id',
                    'industry',
                    'profile',
                    'company_category',
                    'name',
                    'about',
                    'license_number',
                    'website',
                    'email',
                    'phone',
                    'company_type',
                    'dial_code',
                    'profile_picture',
                    'cover_picture',
                    'size',
                    'view_count',
                    'country',
                    'state',
                    'city',
                    'street_address',
                    'longitude',
                    'latitude',
                    'company_status',
                    'created_at',
                    'updated_at',
                    'is_deleted'
                ]

class JobApplyMediaSerializer(serializers.ModelSerializer):
    resume_file = serializers.SerializerMethodField()
    # file_size = serializers.SerializerMethodField()

    def get_resume_file(self, obj):
        if obj.resume_file:
            resume_file_url = obj.resume_file
            return f"{settings.S3_BUCKET_LINK}{resume_file_url}"
        else:
            return None
    
    # def get_file_size(self, obj):
    #     if obj.resume_file:
    #         resume_file_url = obj.resume_file.url

    #         file_url = f"{settings.S3_BUCKET_LINK}{resume_file_url}"
    #         # # file_url = os.path.join(os.path.dirname(os.path.dirname(__file__)),str(resume_file_url))
    #         # size =os.path.getsize(file_url)
    #         # for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
    #         #     if size < 1024.0:
    #         #         return "%3.1f %s" % (size, x)
    #         #     size /= 1024.0
    #         #     return x
    #         return file_url


    class Meta:
        model = JobApplyMedia
        fields = ['id', 'resume_file', 'resume_name', 'resume_extension', 'file_size']

# Get Company Serializer
class GetCompanySerializer(serializers.ModelSerializer):
    logo=serializers.SerializerMethodField()
    profile=DefaultProfileSerializer(read_only=True)
    industry=IndustrySerializer(read_only=True)
    license_file=serializers.SerializerMethodField()
    cover_image=serializers.SerializerMethodField()
    class Meta:
        model = Company
        fields = '__all__'
    
    def get_logo(self, obj):
        request = self.context.get('request')
        if obj.logo:
            logo_url = obj.logo
            return f"{settings.S3_BUCKET_LINK}{logo_url}"
        else:
            return None

    def get_license_file(self, obj):
        request = self.context.get('request')
        if obj.license_file:
            license_file_url = obj.license_file
            return f"{settings.S3_BUCKET_LINK}{license_file_url}"
        else:
            return None

    def get_cover_image(self, obj):
        request = self.context.get('request')
        if obj.cover_image:
            cover_image_url = obj.cover_image
            return f"{settings.S3_BUCKET_LINK}{cover_image_url}"
        else:
            return None

class GetJobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ['id', 'title', 'image']

class JobCategorySerializer(serializers.ModelSerializer):
    total_count = serializers.SerializerMethodField()
    image  = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            return f"{settings.DOMAIN_NAME}{obj.image.url}"
        else:
            return None
 
    def get_total_count(self, obj):
        job = Job.objects.filter(category=obj, is_deleted=False, is_active=True).count()
        return job
    class Meta:
        model = JobCategory
        fields = ['id', 'title', 'image', 'created_at', 'total_count']

# Get Currency Serializer
class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


# Create Job Profile Serializer
class PostJobProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobProfile
        fields = ['id', 'profile', 'background_image', 'image', 'headline', 
                    'description', 'first_name', 'last_name', 'about', 'created_at', 'is_deleted']
    

# Job Profile Serializer
class JobProfileSerializer(serializers.ModelSerializer):
    background_image = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = JobProfile
        fields = ['id', 'profile', 'background_image', 'image', 'headline', 
                    'description', 'first_name', 'last_name', 'about', 'created_at', 'is_deleted']
    
    def get_background_image(self, obj):
        request = self.context.get('request')
        if obj.background_image:
            bg_image_url = obj.background_image
            return f"{settings.S3_BUCKET_LINK}{bg_image_url}"
        else:
            return None

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            image_url = obj.image
            return f"{settings.S3_BUCKET_LINK}{image_url}"
        else:
            return None


# Job Serializer
class JobSerializer(serializers.ModelSerializer):
    job_image = serializers.ListField(required=False, allow_null=True,
                                       child=serializers.FileField(
                                           max_length=1000000, allow_empty_file=True, use_url=False
                                       ))
    job_video = serializers.ListField(required=False, allow_null=True,
                                       child=serializers.FileField(
                                           max_length=1000000, allow_empty_file=True, use_url=False
                                       ))
    class Meta:
        model = Job
        fields = ['id','profile', 'category', 'slug', 'title', 'description', 'job_type', 
        'salary_start', 'salary_end', 'salary_period','position_type','salary_currency', 
        'location', 'longitude', 'latitude', 'job_image', 'job_video', 'dial_code',
        'company_name', 'company_license', 'business_type',]



    def create(self, validated_data):
        """
        Override the create method to add custom validation
        - Create a post with every classified creation.
        - Validate media formats.
        - Create JobMedia objects with every media.
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
            job_images = validated_data.pop('job_image')
        except:
            job_images = None

        # Condition to check maximum number of images.
        if job_images:
            if len(job_images) > 20:
                error = serializers.ValidationError({'success': False, 'response': {
                    'message': 'You can only upload 20 Images for one Job'}})
                error.status_code = 400
                raise error
        try:
            job_videos = validated_data.pop('job_video')
        except:
            job_videos = None

        # Condition to check maximum number of videos.
        if job_videos:
            if len(job_videos) > 1:
                error = serializers.ValidationError({'success': False, 'response': {
                            'message': 'You can only upload 1 Videos for one Job'}})
                error.status_code = 400
                raise error
 
        def create(self, validated_data):
            job = Job.objects.create(**validated_data)
            return job
        job = create(self, validated_data)

        post = Post.objects.create(
            profile=user,
            classified_post=True
        )
        job.post = post
        job.save()

        if job_images is not None:
            for i in job_images:
                name = i.name.split('.')
                if name[-1].strip() in ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG']:
                    JobMedia.objects.create(
                        profile=user,
                        post=post,
                        job=job,
                        job_image=i
                    )
                else:
                    raise serializers.ValidationError({'success': False, 'response': {
                                'message': 'Error in Job Image field,'
                                'Only these formats are allowed {}'.format(
                                ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG'])}})
        if job_videos is not None:
            for job_video in job_videos:
                name = job_video.name.split('.')
                if name[-1] in ['mp4', 'mkv', 'webm', 'avi', 'flv', 'wmv', 'mov', 'MP4', 'MKV', 'WEBM', 'AVI', 'FLV', 'WMV', 'MOV']:
                    if job_video.size > 75000000:
                        error = serializers.ValidationError({'success': False,'response': {
                                    'message': 'Error in Job video size. Maximum allowed size is 75mb.'}})
                        error.status_code = 400
                        raise error
                    else:
                        obj = JobMedia(
                                profile=user,
                                job=job,
                                post=post,
                                job_video=job_video
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
        return job


# Job Project Media Serializer
class JobProjectMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model=JobProjectMedia
        fields="__all__"


# Skill Serializer
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model=Skill
        fields='__all__'

class GetSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model=Skill
        fields='__all__'


# Favourite Serializer
class FavoriteJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteJob
        fields = ['id', 'job', 'profile']

class JobMediaSerializer(serializers.ModelSerializer):
    # job_image = serializers.SerializerMethodField()
    # job_video = serializers.SerializerMethodField()
    # vid_thumbnail = serializers.SerializerMethodField()

    # def get_job_image(self, obj):
    #     if obj.job_image:
    #         return f"{settings.S3_BUCKET_LINK}{obj.job_image.url}"
    #     else:
    #         return None

    # def get_job_video(self, obj):
    #     if obj.job_video:
    #         return f"{settings.S3_BUCKET_LINK}{obj.job_video.url}"
    #     else:
    #         return None

    # def get_vid_thumbnail(self, obj):
    #     if obj.vid_thumbnail:
    #         return f"{settings.S3_BUCKET_LINK}{obj.vid_thumbnail.url}"
    #     else:
    #         return None
    def to_representation(self, obj):
        return_dict = dict()
        if obj.job_image:
            return_dict['id'] = obj.id
            return_dict['job_image'] = f"{settings.S3_BUCKET_LINK}{obj.job_image}"
        if obj.job_video:
            return_dict['id'] = obj.id
            return_dict['job_video'] = f"{settings.S3_BUCKET_LINK}{obj.job_video}"
            if obj.vid_thumbnail:
                return_dict['id'] = obj.id
                return_dict['vid_thumbnail'] = f"{settings.S3_BUCKET_LINK}{obj.vid_thumbnail}"
            else:
                return_dict['vid_thumbnail'] = ''
        return return_dict
    class Meta:
        model = JobMedia
        fields = ['id', 'job_image', 'job_video', 'vid_thumbnail']
        

class JobImageMediaSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.job_image:
            return f"{settings.S3_BUCKET_LINK}{obj.job_image}"
    class Meta:
        model = JobMedia
        fields = ['id', 'image']


class JobVideoMediaSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()
    video_thumbnail = serializers.SerializerMethodField()

    def get_video(self, obj):
        if obj.job_video:
            return f"{settings.S3_BUCKET_LINK}{obj.job_video}"

    def get_video_thumbnail(self, obj):
        if obj.vid_thumbnail:
            return f"{settings.S3_BUCKET_LINK}{obj.vid_thumbnail}"
    class Meta:
        model = JobMedia
        fields = ['id','video' , 'video_thumbnail']

# Get Job Serializer 
class GetJobSerializer(serializers.ModelSerializer):
    profile = DefaultProfileSerializer(read_only=True)
    salary_currency = CurrencySerializer(read_only=True)
    image_media = serializers.SerializerMethodField()
    video_media = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    is_applied = serializers.SerializerMethodField()
    total_saved = serializers.SerializerMethodField()

    def get_total_saved(self, job):
        favourite = FavoriteJob.objects.filter(job=job).count()
        if favourite:
            return favourite
        else:
            return None

    def get_is_applied(self, obj):
        profile = self.context.get('profile')
        try:
            job = Job.objects.get(id=obj.id, jobapply_job__profile=profile, is_deleted=False)
            return True
        except:
            return False

    def get_is_favourite(self, job):
        try:
            profile = self.context.get("profile")
            favourite = FavoriteJob.objects.get(job=job, profile=profile)
            return True
        except:
            return False

    def get_company(self, job):
        if job.business_type == 'Company':
            try:
                company = Company.objects.get(profile=job.profile, company_type='Job')
                return CompanySerializer(company).data
            except Exception as e:
                print(e)
                return None

    def get_category(self, job):
        return GetJobCategorySerializer(job.category).data

    def get_media(self, obj):
        media = JobMedia.objects.filter(job=obj, is_deleted=False)
        return JobMediaSerializer(media, many=True).data

    def get_image_media(self, obj):
        return JobImageMediaSerializer(obj.jobmedia_job.filter(is_deleted=False).exclude(job_image=''), many=True).data

    def get_video_media(self, obj):
        return JobVideoMediaSerializer(obj.jobmedia_job.filter(is_deleted=False).exclude(job_video=''), many=True).data
    class Meta:
        model = Job
        fields = [
                'id', 'profile', 'category', 'slug', 'title', 'description', 'job_type', 'company',
                'business_type', 'salary_start', 'salary_end', 'salary_period', 'dial_code', 'view_count', 'total_saved',
                'mobile', 'position_type','salary_currency', 'created_at', 'location', 'longitude', 'latitude', 
                'image_media', 'video_media', 'is_favourite', 'is_applied', 'verification_status', 'is_active'
        ]

    def get_total_apply(self, obj):
        apply = JobApply.objects.filter(job=obj, is_deleted=False, is_active=True).count()
        return apply

    def get_is_favourite(self, obj):
        jobprofile = self.context.get("jobprofile")
        try:
            favourite = FavoriteJob.objects.get(job=obj, jobprofile=jobprofile)
            return True
        except Exception as e:
            print(e)
            return False
        
    def get_my_jobs(self, obj):
        jobprofile = self.context.get("jobprofile")
        myjobs = Job.objects.filter(jobprofile=jobprofile)
        total_my_jobs=myjobs.count()
        return total_my_jobs

# Get Favourite Job Serializer 
class GetFavoriteJobSerializer(serializers.ModelSerializer):
    job=serializers.SerializerMethodField()
    jobprofile=JobProfileSerializer(read_only=True)
    

    def get_job(self, obj):
        fav_job = GetJobSerializer(obj.job, read_only=True , context=self.context)
        data = fav_job.data
        data['is_favourite'] = True
        return data

    class Meta:
        model = FavoriteJob
        fields = '__all__'


# Job Apply Serializer
class JobApplySerializer(serializers.ModelSerializer):
    class Meta:
        model=JobApply
        fields = [
            'id', 'profile', 'job', 'full_name', 'mobile', 'email', 'dial_code',
            'cover_letter', 'resume', 'created_at', 'updated_at']


# Job Project Serializer
class JobProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobProject
        fields = "__all__"


# Default Job Profile Serializer
class DefaultJobProfileSerializer(serializers.ModelSerializer):
    profile = DefaultProfileSerializer(read_only=True)
    image = serializers.SerializerMethodField()

    def get_background_image(self, obj):
        request = self.context.get('request')
        if obj.background_image:
            bg_image_url = obj.background_image
            return f"{settings.S3_BUCKET_LINK}{bg_image_url}"
        else:
            return None

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            image_url = obj.image
            return f"{settings.S3_BUCKET_LINK}{image_url}"
        else:
            return None


    class Meta:
        model=JobProfile
        fields = ['id', 'profile', 'image', 'headline', 'first_name', 'last_name']


# Get Job Apply Serializer
class GetJobApplySerializer(serializers.ModelSerializer):
    resume = serializers.SerializerMethodField()
    job = GetJobSerializer(read_only=True)

    def get_resume(self, obj):
        # try:
        #     media = JobApplyMedia.objects.get(apply=obj)
        #     return f"{settings.S3_BUCKET_LINK}{media.resume_file}"
        # except:
        if obj.resume:
            return f"{settings.S3_BUCKET_LINK}{obj.resume}"
        else:
            return None

    class Meta:
        model=JobApply
        fields = [
            'id', 'profile', 'job', 'full_name', 'mobile', 'email',
            'cover_letter', 'created_at', 'updated_at', 'resume' ,'dial_code'
            ]

    
# Get Job Profile Serialzer
class GetJobProfileSerializer(serializers.ModelSerializer):
    skill=GetSkillSerializer(read_only=True,many=True)
    profile=DefaultProfileSerializer(read_only=True)
    added_jobs=serializers.SerializerMethodField()
    applied_jobs=serializers.SerializerMethodField()
    favourite_jobs=serializers.SerializerMethodField()
    job_project = serializers.SerializerMethodField()
    experience=serializers.SerializerMethodField()
    education=serializers.SerializerMethodField()
    edoresement=serializers.SerializerMethodField()
    background_image=serializers.SerializerMethodField()
    image=serializers.SerializerMethodField()

    class Meta:
        model=JobProfile
        fields='__all__'

    def get_favourite_jobs(self, obj):
        favourite = FavoriteJob.objects.filter(jobprofile=obj)
        fav_jobs=favourite.count()
        return fav_jobs


    def get_added_jobs(self, obj):
        jobs = Job.objects.filter(jobprofile=obj)
        total_jobs=jobs.count()
        return total_jobs

    def get_background_image(self, obj):
        request = self.context.get('request')
        if obj.background_image:
            background_image_url = obj.background_image
            return f"{settings.S3_BUCKET_LINK}{background_image_url}"
        else:
            return None

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            image_url = obj.image
            return f"{settings.S3_BUCKET_LINK}{image_url}"
        else:
            return None

    def get_applied_jobs(self, obj):
        appply_jobs = JobApply.objects.filter(jobprofile=obj)
        total_apply_jobs=appply_jobs.count()
        return total_apply_jobs


    def get_job_project(self, obj):
        jobproject=JobProject.objects.filter(jobprofile=obj, is_deleted=False).order_by("-created_at")
        serializer=GetJobProjectSerializer(jobproject, many=True)
        return serializer.data

                         
    def get_experience(self, obj):
        experience=UserWorkPlace.objects.filter(profile=obj.profile)
        serializer=UserWorkPlaceSerializer(experience, many=True)
        return serializer.data


    def get_education(self, obj):
        education=UserHighSchool.objects.filter(profile=obj.profile)
        serializer=UserHighSchoolSerializer(education, many=True)
        return serializer.data


    def get_edoresement(self, obj):
        endoresement=JobEndoresements.objects.filter(profile1=obj)
        serializer=JobEndoresementsSerializer(endoresement, many=True)
        return serializer.data


# Job Project Serialzer
class JobProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model=JobProject
        fields='__all__'


# Get Job Project Media Serializer
class GetJobProjectMediaSerialzer(serializers.ModelSerializer):
    
    class Meta:
        model = JobProjectMedia
        fields = ['id', 'image', 'video', 'vid_thumbnail']

    
    def to_representation(self, obj):
        return_dict = dict()
        if obj.vid_thumbnail:
            return_dict['id'] = obj.id
            return_dict['vid_thumbnail'] = f"{settings.S3_BUCKET_LINK}{obj.vid_thumbnail}"
        if obj.image:
            return_dict['id'] = obj.id
            return_dict['image'] = f"{settings.S3_BUCKET_LINK}{obj.image}"
        if obj.video:
            return_dict['id'] = obj.id
            return_dict['video'] = f"{settings.S3_BUCKET_LINK}{obj.video}"
        return return_dict


# Get Job Project Serializer
class GetJobProjectSerializer(serializers.ModelSerializer):
    jobprofile = DefaultJobProfileSerializer(read_only=True)
    media = serializers.SerializerMethodField()
    
    class Meta:
        model = JobProject
        fields = ['id', 'name', 'description', 'media', 'jobprofile', 'created_at']

    def get_media(self, obj):
        jobproject_media = JobProjectMedia.objects.filter(jobproject=obj)
        serializer = GetJobProjectMediaSerialzer(jobproject_media, many=True)
        return serializer.data


# Get Job Alert Serializer
class JobAlertSerializer(serializers.ModelField):
    class Meta:
        model=JobAlert
        fields='__all__'


# Get Single Job Serializer
class GetSingleJobSerializer(serializers.ModelSerializer):
    jobprofile = serializers.SerializerMethodField()
    contact_person = DefaultProfileSerializer(read_only=True)
    skill = GetSkillSerializer(read_only=True, many=True)
    is_favourite = serializers.SerializerMethodField()
    my_jobs = serializers.SerializerMethodField()
    salary_currency = CurrencySerializer(read_only=True)
    contact_person = DefaultProfileSerializer(read_only=True)
    company = GetCompanySerializer(read_only=True)
    country = CountrySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    language = LanguageSerializer(read_only=True)
    industry = IndustrySerializer(read_only=True)
    applications = serializers.SerializerMethodField()


    class Meta:
        model=Job
        fields='__all__'

    def get_jobprofile(self, obj):
        profile = self.context.get("profile")
        try:
            jobprofile = JobProfile.objects.get(profile=profile, is_deleted=False)
        except Exception as e:
            jobprofile = None
        serializer = JobProfileSerializer(jobprofile)
        return serializer.data

    def get_is_favourite(self, obj):
        jobprofile = self.context.get("jobprofile")
        try:
            favourite = FavoriteJob.objects.get(job=obj, jobprofile=jobprofile)

            return True
        except:
            return False
        
    def get_my_jobs(self, obj):
        jobprofile = self.context.get("jobprofile")
        myjobs = Job.objects.filter(jobprofile=jobprofile, is_deleted=False)
        total_my_jobs=myjobs.count()
        return total_my_jobs

    def get_applications(self, obj):
        applications = JobApply.objects.filter(job=obj)
        return GetJobApplySerializer(applications, many=True).data


# Get Similar Job Serializer
class GetSimilarJobSerializer(serializers.ModelSerializer):
    jobprofile=JobProfileSerializer(read_only=True)
    contact_person=DefaultProfileSerializer(read_only=True)
    class Meta:
        model=Job
        fields='__all__'


# Get Job Notification Serializer
class GetJobNotificationSerializer(serializers.ModelSerializer):
    notifiers_list=DefaultProfileSerializer(read_only=True, many=True)
    class Meta:
        model=Notification
        fields='__all__'


# Get Story Serializer 
class JobStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobStory
        fields = '__all__'


# Get Single Job Story Serializer
class GetSingleJobStorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    video_thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = JobStory
        fields = ['id' ,'jobprofile', 'text','description' ,'font_family', 'background_color',
                  'text_color', 'image', 'video', 'video_thumbnail', 'x_axis', 'y_axis', 'angle', 'story_type', 'created_at', 'privacy',
                  'post_id']

    def get_profile(self, obj):
        return DefaultProfileSerializer(obj.profile).data

    def get_image(self, obj):
        if obj.image:
            image = f"{settings.S3_BUCKET_LINK}{obj.image}"
        else:
            image = None
        return image

    def get_video_thumbnail(self, obj):
        if obj.video_thumbnail:
            video_thumbnail = f"{settings.S3_BUCKET_LINK}{obj.video_thumbnail}"
        else:
            video_thumbnail = None
        return video_thumbnail

    def get_video(self, obj):
        if obj.video:
            video = f"{settings.S3_BUCKET_LINK}{obj.video}"
        else:
            video = None
        return video


# Job Endoresements Serializer
class JobEndoresementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobEndoresements
        fields = "__all__"


# Get Job Endoresement Serializer
class GetJobEndoresementsSerializer(serializers.ModelSerializer):
    profile1 = JobProfileSerializer(read_only=True)
    profile2 = DefaultProfileSerializer(read_only=True)
    class Meta:
        model = JobEndoresements
        fields = "__all__"


# Get Job Search History Serializer
class GetJobSearchHistorySerializer(serializers.ModelSerializer):
    job=JobSerializer(read_only=True)
    class Meta:
        model = JobSearchHistory
        fields = "__all__"


# Get Job Project Media Serializer
class GetJobProjectMediaSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    vid_thumbnail = serializers.SerializerMethodField()    
    class Meta:
        model = JobProjectMedia
        fields = "__all__"

    def get_image(self, obj):
        if obj.image:
            image_url = obj.image
            return f"{settings.S3_BUCKET_LINK}{image_url}"
        else:
            return None

    def get_video(self, obj):
        if obj.video:
            video_url = obj.video
            return f"{settings.S3_BUCKET_LINK}{video_url}"
        else:
            return None

    def get_vid_thumbnail(self, obj):
        if obj.vid_thumbnail:
            vid_thumbnail_url = obj.vid_thumbnail
            return f"{settings.S3_BUCKET_LINK}{vid_thumbnail_url}"
        else:
            return None


class ReportJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportJob
        fields = '__all__'