from random import choices
import uuid
from django.db import models
from youonline_social_app.constants import  create_slug
from youonline_social_app.models import *
from automotive_app.models import Automotive
from youonline_social_app.constants import s3_compress_image
from property_app.models import Property
import tempfile

# Create your models here.
class Industry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=512, null=True, blank=True)

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name


    class Meta:
        db_table='Industry'

class JobCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=500, null=True, blank=True)
    image = models.FileField(null=True, blank=True, upload_to='category/images')
    
    view_count = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return str(self.title)

    class Meta:
        db_table = 'JobCategory'

class CompanyCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=500, null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to='category/images')

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return str(self.title)

    class Meta:
        db_table = 'CompanyCategory'


class Company(models.Model):
    COMPANY_CHOICES = [
        ('Classified', 'Classified'),
        ('Automotive', 'Automotive'),
        ('Job','Job'),
        ('Property', 'Property'),

    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, null=True, blank=True)

    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True, related_name='company_profile')

    company_category = models.ForeignKey(CompanyCategory, on_delete=models.CASCADE, null=True, blank=True, related_name='company_profile')

    name = models.CharField(max_length=512, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    
    license_number = models.CharField(max_length=512, null=True, blank=True)
    website = models.CharField(max_length=512, null=True, blank=True)
    email = models.EmailField(max_length=256, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    company_type = models.CharField(max_length=200, choices=COMPANY_CHOICES, blank=True, null=True)
    dial_code = models.CharField(max_length=200, blank=True, null=True)
    size = models.IntegerField(null=True, blank=True)
    view_count = models.BigIntegerField(default=0)

    # Location
    country = models.ForeignKey('youonline_social_app.Country', on_delete=models.CASCADE, null=True, blank=True)
    state = models.ForeignKey('youonline_social_app.State', on_delete=models.CASCADE, null=True, blank=True)
    city = models.ForeignKey('youonline_social_app.City', on_delete=models.CASCADE, null=True, blank=True)
    
    street_address = models.TextField(null=True, blank=True)
    longitude = models.CharField(max_length=512, null=True, blank=True)
    latitude = models.CharField(max_length=512, null=True, blank=True)
    company_status = models.BooleanField(default=True)
    # WHO Columns

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table='Company'

    
    def __str__(self):
        return str(self.name)


class Currency(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    country = models.ForeignKey('youonline_social_app.Country', on_delete=models.CASCADE, null=True, blank=True, related_name="currency_country")
    name = models.CharField(max_length=64, null=True, blank=True)
    code = models.CharField(max_length=16, null=True, blank=True)
    currency_symbol = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table='Currency'


class Skill(models.Model):
    skill = models.CharField(max_length=200)
    is_deleted=models.BooleanField(default=False)

    def __str__(self):
        return self.skill

    class Meta:
        db_table = 'Skill'


class JobProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    skill = models.ManyToManyField(Skill, blank=True)
    profile = models.OneToOneField('youonline_social_app.Profile',null=True, blank=True, on_delete=models.CASCADE)
    background_image = models.ImageField(max_length=255, upload_to='JobProfile/image/%Y/%m' ,null=True, blank=True)
    image = models.ImageField(max_length=255, upload_to='JobProfile/image/%Y/%m' ,null=True, blank=True)
    headline = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=10000, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)

    
    class Meta:
        db_table='JobProfile'
    
    def __str__(self):
        return str(self.profile)


class Job(models.Model):
    job_choices = [
        ('Part Time', 'Part Time'),
        ('Full Time', 'Full Time'),
        ('Contract','Contract'),

        ('Remote', 'Remote'),
        ('In-Office', 'In-Office'),
        ('Hybrid','Hybrid')
    ]
    employee_choices = [
        ('Fresh', 'Fresh'),
        ('Intermediate', 'Intermediate'),
        ('Senior', 'Senior'),
      
    ]
    duration_choices = [
        ('7 days', '7 days'),
        ('15 days', '15 days'),
        ('None', 'None'), 
    ]
    salary_choices = [
        ('Hourly', 'Hourly'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'), 
        ('Yearly', 'Yearly'), 
    ]
    position_choices = [
        ('Part Time', 'Part Time'),
        ('Full Time', 'Full Time'),
        ('Contract','Contract'),
        ('Temporary','Temporary'),
    ]
    VERIFICATION_STATUS = [
        ('Pending', 'Pending'),
        ('Verified', 'Verified'),
        ('Rejected', 'Rejected'),
    ]
    
    BUSINESS_CHOICES = [
        ('Individual', 'Individual'),
        ('Company', 'Company'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # ForeignKey
    skill = models.ManyToManyField(Skill, blank=True, related_name='job_skill')
    jobprofile = models.ForeignKey(JobProfile, null=True, blank=True, on_delete=models.CASCADE)
    profile = models.ForeignKey('youonline_social_app.Profile', null=True, blank=True, on_delete=models.CASCADE, related_name='job_profile')
    post = models.ForeignKey('youonline_social_app.Post', on_delete=models.CASCADE, null=True, blank=True, related_name="jobs_post")
    category = models.ForeignKey(JobCategory, null=True, blank=True, on_delete=models.CASCADE)

    company_name = models.CharField(max_length=512, null=True, blank=True)
    company_license = models.CharField(max_length=512, null=True, blank=True)

    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    title = models.CharField(max_length=512, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    employment_type = models.CharField(max_length=30,choices=employee_choices, null=True, blank=True)
    job_type = models.CharField(max_length=255, choices=job_choices ,null=True, blank=True)
    
    salary_start_range = models.IntegerField(null=True, blank=True)
    salary_end_range = models.IntegerField(null=True, blank=True)

    salary_start = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_end = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_period =  models.CharField(max_length=512, choices=salary_choices, null=True, blank=True)
    position_type =  models.CharField(max_length=512, choices=position_choices, null=True, blank=True)

    salary_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True, blank=True)
    min_experience =  models.CharField(max_length=512, null=True, blank=True)
    max_experience =  models.CharField(max_length=512, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    dial_code = models.CharField(max_length=200, blank=True, null=True)

    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='job_company')
    contact_person = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True, related_name='job_contact_person')
    country = models.ForeignKey('youonline_social_app.Country', on_delete=models.CASCADE, null=True, blank=True)
    state = models.ForeignKey('youonline_social_app.State', on_delete=models.CASCADE, null=True, blank=True)
    city = models.ForeignKey('youonline_social_app.City', on_delete=models.CASCADE, null=True, blank=True)
    language = models.ForeignKey('youonline_social_app.Language', on_delete=models.CASCADE, null=True, blank=True)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, null=True, blank=True)
    is_promoted = models.BooleanField(default=False)
    view_count = models.BigIntegerField(default=0)

    education = models.CharField(max_length=512, null=True, blank=True)
    job_duration = models.CharField(max_length=30,choices=duration_choices, null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    longitude = models.CharField(max_length=512, null=True, blank=True)
    latitude = models.CharField(max_length=512, null=True, blank=True)
    mobile = models.CharField(max_length=255, null=True, blank=True)
    verification_status = models.CharField(max_length=255, choices=VERIFICATION_STATUS, default='Pending', null=True, blank=True)
    business_type = models.CharField(max_length=255, choices=BUSINESS_CHOICES, null=True, blank=True)
    
    long = models.DecimalField(max_digits=30, decimal_places=16, null=True, blank=True)
    lat = models.DecimalField(max_digits=30, decimal_places=16,  null=True, blank=True)
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_by = models.CharField(max_length=64, null=True, blank=True)
    updated_by = models.CharField(max_length=64, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            slugs = list(Job.objects.all().values_list('slug', flat=True))
            self.slug = create_slug(title=self.title, slugs=slugs)
        super(Job, self).save(*args, **kwargs)


    def __str__(self):
        return self.title


    class Meta:
        db_table='Job'


class JobMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    profile = models.ForeignKey('youonline_social_app.Profile', null=True, blank=True, on_delete=models.CASCADE, related_name='jobmedia_profile')

    post = models.ForeignKey('youonline_social_app.Post', on_delete=models.CASCADE, null=True, blank=True, related_name='jobmedia_post')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True, related_name='jobmedia_job')
    # Media
    job_image = models.ImageField(max_length=256, upload_to='Job_images/%Y/%m', null=True)
    job_video = models.FileField(max_length=256, upload_to='Job_video/%Y/%m', null=True)
    vid_thumbnail = models.FileField(max_length=256, upload_to='Job_video/%Y/%m', null=True)
    is_deleted = models.BooleanField(default=False)
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_compressed = models.BooleanField(default=False)
    video_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)

    def __str__(self):
        return str(self.job)

    def save(self, *args, **kwargs):
        if self.job_image and not self.is_compressed:
            self.job_image = s3_compress_image(self.job_image)
            self.is_compressed = True
        # Generate Video Thumnail
        if self.job_video and not self.vid_thumbnail:
            # Get Temporary File Path
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_path = temp_file.name
            with open(temp_path, 'wb+') as destination:
                 for chunk in self.job_video.chunks():
                           destination.write(chunk)
            # Instantiate VideoFileClip object
            clip = VideoFileClip(temp_path)
            # Get video frame at 1 second
            temp_thumb = clip.get_frame(1)
            # Convert numpy array to pillow image and compress it
            self.vid_thumbnail = generate_video_thumbnail(temp_thumb)
        super(JobMedia, self).save(*args, **kwargs)

    class Meta:
        db_table = 'JobMedia'


# class JobView(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
#     job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="jobview_job")
#     viewer = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, related_name="jobview_viewer", null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

#     class Meta:
#         db_table = 'JobView'

#     def __str__(self):
#         return f"{self.job.title} viewed by {self.viewer.user.username}"

class JobApply(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey('youonline_social_app.Profile', null=True, blank=True, on_delete=models.CASCADE, related_name='jobapply_profile')

    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True, related_name="jobapply_job")
    full_name = models.CharField(max_length=512, null=True, blank=True)

    dial_code = models.CharField(max_length=512, null=True, blank=True)
    mobile = models.CharField(max_length=512, null=True, blank=True)
    email = models.EmailField(verbose_name="email", max_length=60, null=True, blank=True)
    education = models.CharField(max_length=512, null=True, blank=True)
    resume = models.ForeignKey('job_app.JobApplyMedia', on_delete=models.CASCADE, null=True, blank=True, related_name="jobapply_job")
    cover_letter = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'JobApply'
        unique_together = ('profile', 'job')

    def __str__(self):
        return str(self.job) 


class JobApplyMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey('youonline_social_app.Profile', null=True, blank=True, on_delete=models.CASCADE, related_name='jobapplymedia_profile')

    resume_file = models.FileField(upload_to='Apply_Jobs/Resume/%Y/%m',null=True, blank=True)
    resume_name = models.CharField(max_length=512, null=True, blank=True)
    file_size = models.CharField(max_length=100, null=True, blank=True)
    resume_extension = models.CharField(max_length=55, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table='JobApplyMedia'

class FavoriteJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    jobprofile = models.ForeignKey(JobProfile, on_delete=models.CASCADE, null=True, blank=True)
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True, related_name='favoritejob_profile')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True, related_name='favoritejob_job')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.profile)

    class Meta:
        db_table='FavoriteJob'
        unique_together = ('profile', 'job')

class JobProject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    jobprofile = models.ForeignKey(JobProfile, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField( null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    post = models.ForeignKey('youonline_social_app.Post', on_delete=models.CASCADE, null=True, blank=True)
    associated_with = models.ForeignKey('youonline_social_app.UserWorkPlace', on_delete=models.CASCADE, null=True, blank=True)
    project_url = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return (self.name)

    class Meta:
        db_table='JobProject'


class JobProjectMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    jobprofile = models.ForeignKey(JobProfile, on_delete=models.CASCADE, null=True, blank=True)
    jobproject = models.ForeignKey(JobProject, on_delete=models.CASCADE, null=True, blank=True, related_name='jobprojectmedia_jobproject')
    # Media
    image = models.ImageField(max_length=255, upload_to='JobProject/images/%Y/%m', null=True, blank=True)
    video = models.FileField(max_length=255, upload_to='JobProject/videos/%Y/%m', null=True, blank=True)
    vid_thumbnail = models.FileField(max_length=255, upload_to='JobProject/thumbnail/%Y/%m', null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_compressed = models.BooleanField(default=False)
    video_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'JobProjectMedia'


    def save(self, *args, **kwargs):
        # Compress Image
        if self.image and not self.is_compressed:
            self.mage = s3_compress_image(self.image)
            self.is_compressed = True
        # Generate Video thumbnail
        if self.video and not self.vid_thumbnail:
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_path = temp_file.name
            with open(temp_path, 'wb+') as destination:
                 for chunk in self.video.chunks():
                           destination.write(chunk)
            clip = VideoFileClip(temp_path)
            temp_thumb = clip.get_frame(1)
            self.vid_thumbnail = generate_video_thumbnail(temp_thumb)
        super(JobProjectMedia, self).save(*args, **kwargs)


class JobAlert(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    jobprofile = models.ForeignKey(JobProfile, on_delete=models.CASCADE, null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    skill = models.ManyToManyField(Skill, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'JobAlert'


class JobSearchHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True, related_name='jobsearchhistory_job')
    jobprofile = models.ForeignKey(JobProfile, on_delete=models.CASCADE, null=True, blank=True)

    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True, related_name='jobsearchhistory_profile')

    skill = models.CharField(max_length=1000,null=True, blank=True)
    location = models.CharField(max_length=1000, null=True, blank=True)
    employment_type = models.CharField(max_length=1000, null=True, blank=True)
    salary_start_range = models.IntegerField(null=True, blank=True)
    salary_end_range = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'JobSearchHistory'


class JobStory(models.Model):
    STORY_CHOICES = [
        ("Text", "Text"),
        ("Media", "Media")
    ]

    YOUONLINE_PRIVACY_CHOICES = [
        ('Public', 'Public'),
        ('OnlyMe', 'OnlyMe'),
        ('Friends', 'Friends'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    jobprofile = models.ForeignKey(JobProfile, on_delete=models.CASCADE)
    post = models.ForeignKey('youonline_social_app.Post', on_delete=models.CASCADE, null=True, blank=True)
    text = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    font_family = models.CharField(max_length=128, null=True, blank=True)
    background_color = models.CharField(max_length=128, null=True, blank=True)
    text_color = models.CharField(max_length=128, null=True, blank=True)
    image = models.ImageField(upload_to='JobStories/images/%Y/%m', null=True, blank=True)
    video = models.FileField(upload_to='JobStories/videos/%Y/%m', null=True, blank=True)
    video_thumbnail = models.ImageField(upload_to='JobStories/%Y/%m', null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    x_axis = models.FloatField(default=0.00)
    y_axis = models.FloatField(default=0.00)
    angle = models.FloatField(default=0.00)
    story_type = models.CharField(max_length=32, choices=STORY_CHOICES, default="Text")
    privacy = models.CharField(max_length=32, choices=YOUONLINE_PRIVACY_CHOICES, default="Public")
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_compressed = models.BooleanField(default=False)
    video_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)

    class Meta:
        db_table = 'JobStory'

    def __str__(self):
        return self.jobprofile.profile.user.username


    def save(self, *args, **kwargs):
        # Compress Image
        if self.image and not self.is_compressed:
            self.mage = s3_compress_image(self.image)
            self.is_compressed = True
        # Generate Video thumbnail
        if self.video and not self.video_thumbnail:
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_path = temp_file.name
            with open(temp_path, 'wb+') as destination:
                 for chunk in self.video.chunks():
                           destination.write(chunk)
            clip = VideoFileClip(temp_path)
            temp_thumb = clip.get_frame(1)
            self.video_thumbnail = generate_video_thumbnail(temp_thumb)
        super(JobStory, self).save(*args, **kwargs)


class JobEndoresements(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile1 = models.ForeignKey(JobProfile, null=True, blank=True, on_delete=models.CASCADE)
    profile2 = models.ForeignKey('youonline_social_app.Profile', on_delete=models.SET_NULL, null=True, blank=True)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'JobEndoresements'

    def __str__(self):
        return self.text



class CompanyLogo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE, related_name='companylogo_company')

    logo = models.ImageField(max_length=256, upload_to='company/logo/%Y/%m', null=True)
    is_deleted = models.BooleanField(default=False)
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_compressed = models.BooleanField(default=False)
    video_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)

    def __str__(self):
        return str(self.company)

    def save(self, *args, **kwargs):
        if self.logo and not self.is_compressed:
            self.logo = s3_compress_image(self.logo)
            self.is_compressed = True
        super(CompanyLogo, self).save(*args, **kwargs)

    class Meta:
        db_table = 'CompanyLogo'


class CompanyCoverImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # Foreign Keys
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE, related_name='companycoverimage_company')

    cover_image = models.ImageField(max_length=256, upload_to='comapny/cover_image/%Y/%m', null=True)
    is_deleted = models.BooleanField(default=False)
    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    is_compressed = models.BooleanField(default=False)
    video_compressed = models.BooleanField(default=False)
    bucket_uploaded = models.BooleanField(default=False)

    def __str__(self):
        return str(self.company)

    def save(self, *args, **kwargs):
        if self.cover_image and not self.is_compressed:
            self.cover_image = s3_compress_image(self.cover_image)
            self.is_compressed = True
        super(CompanyCoverImage, self).save(*args, **kwargs)

    class Meta:
        db_table = 'CompanyCoverImage'


class ReportJob(models.Model):
    REPORT_CHOICES = [
        ('Fraud', 'Fraud'),
        ('Offensive content', 'Offensive content'),
        ('Duplicate ad', 'Duplicate ad'),
        ('Product alread sold', 'Product alread sold'),
        ('Other', 'Other'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    profile = models.ForeignKey('youonline_social_app.Profile', on_delete=models.CASCADE, null=True, blank=True, related_name="reportjob_profile")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True, related_name="reportjob_job")
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    report_type = models.CharField(max_length=255, choices=REPORT_CHOICES, default='Other', null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.job)

    class Meta:
        db_table = 'ReportJob'
 