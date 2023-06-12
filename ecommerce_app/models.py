from itertools import product
from django.db import models
from youonline_social_app.models import *
from community_app.models import *
from youonline_social_app.constants import create_slug

# Create your models here.
class BusinessOwner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name="businessowner_profile")
    business_email = models.EmailField(max_length=128, null=True, blank=True)
    full_name = models.CharField(max_length=32, null=True, blank=True)
    profile_picture = models.ImageField(max_length=512, upload_to='BusinessOwnerProfile', null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="businessowner_country")
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name="businessowner_city")
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.profile)

    class Meta:
        db_table = 'BusinessOwner'
        verbose_name_plural = 'Business Owners'


    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = f"{self.profile.user.first_name} {self.profile.user.last_name}"
        if not self.business_email:
            self.business_email = f"{self.profile.user.email}"
        try:
            self.profile_picture = s3_compress_image(self.profile_picture)
        except:
            pass
        super(BusinessOwner, self).save(*args, **kwargs)


class BusinessDetails(models.Model):
    CHECKOUT_CHOICES = [
        ('CashOnDelivery', 'Cash On Delivry'),
        ('Website', 'Website'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(BusinessOwner, on_delete=models.PROTECT, related_name="businessdetails_owner")
    page = models.OneToOneField(Page, on_delete=models.PROTECT, null=True, blank=True, related_name="businessdetails_page")
    name = models.CharField(max_length=32, null=True, blank=True)
    description = models.TextField(max_length=512, null=True, blank=True)
    address = models.CharField(max_length=128, null=True, blank=True)
    phone = models.CharField(max_length=32, null=True, blank=True)
    email = models.EmailField(max_length=128, null=True, blank=True)
    checkout_option = models.CharField(max_length=32, choices=CHECKOUT_CHOICES, default='CashOnDelivery')
    is_approved = models.BooleanField(default=False)
    countries = models.TextField(max_length=512, null=True, blank=True)
    # URL Links
    website = models.CharField(max_length=128, null=True, blank=True)
    facebook = models.CharField(max_length=128, null=True, blank=True)
    twitter = models.CharField(max_length=128, null=True, blank=True)
    instagram = models.CharField(max_length=128, null=True, blank=True)
    youtube = models.CharField(max_length=128, null=True, blank=True)
    linkedin = models.CharField(max_length=128, null=True, blank=True)
    google = models.CharField(max_length=128, null=True, blank=True)
    
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.owner)

    class Meta:
        db_table = 'BusinessDetails'
        verbose_name_plural = 'Business Details'


    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.page.name
        if not self.email:
            self.email = self.owner.business_email
        if not self.address:
            self.address = self.page.street_adress
        super(BusinessDetails, self).save(*args, **kwargs)


class ProductCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=64)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "ProductCategory"
        verbose_name_plural = "Product Categories"


class ProductSubCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, related_name="productsubcategory_category")
    title = models.CharField(max_length=64)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "ProductSubCategory"
        verbose_name_plural = "Product Sub Categories"


class Product(models.Model):
    PUBLISH_STATUS_CHOICES = [
        ('Published', 'Published'),
        ('Draft', 'Draft'),
        ('Scheduled', 'Scheduled'),
    ]


    # Product Details
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    business_details = models.ForeignKey(BusinessDetails, on_delete=models.PROTECT, related_name="product_businessdetails")
    post = models.ForeignKey(Post, on_delete=models.PROTECT, null=True, blank=True, related_name="post_product")
    title = models.CharField(max_length=32, null=True, blank=True, default="")
    description = models.TextField(max_length=512, null=True, blank=True, default="")
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, null=True, blank=True, related_name="product_category")
    subcategory = models.ForeignKey(ProductSubCategory, on_delete=models.PROTECT, null=True, blank=True, related_name="product_subcategory")
    brand = models.CharField(max_length=128, null=True, blank=True, default="")
    url = models.CharField(max_length=128, null=True, blank=True, default="")
    color = models.CharField(max_length=128, null=True, blank=True, default="")
    size = models.CharField(max_length=128, null=True, blank=True, default="")
    condition = models.CharField(max_length=128, null=True, blank=True, default="")
    material = models.CharField(max_length=128, null=True, blank=True, default="")
    status = models.BooleanField(default=True)
    publish_status = models.CharField(max_length=32, choices=PUBLISH_STATUS_CHOICES, default='Published')
    quantity = models.IntegerField(default=0)
    availability = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    # Financial Details
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # Creation Time
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "Product"
        verbose_name_plural = "Products"


    def save(self, *args, **kwargs):
        if not self.url:
            slugs = Product.objects.values_list('url', flat=True)
            self.url = create_slug(title=self.title, slugs=slugs)
        super(Product, self).save()


class ProductSchedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="productschedule_product")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="productschedule_profile")
    publish_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return str(self.product)

    class Meta:
        db_table = "ProductSchedule"
        verbose_name_plural = "Product Schedules"


class ProductMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="productmedia_product")
    image = models.ImageField(max_length=512, upload_to='ProductImages', null=True, blank=True)
    image_thumbnail = models.ImageField(max_length=512, upload_to='ProductImages', null=True, blank=True)
    image_compressed = models.BooleanField(default=False)
    video = models.FileField(max_length=512, upload_to='ProductVideos', null=True, blank=True)
    video_thumbnail = models.ImageField(max_length=512, upload_to='ProductVideos', null=True, blank=True)
    video_compressed = models.BooleanField(default=False)
    youtube = models.CharField(max_length=128, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return str(self.product)

    def save(self, *args, **kwargs):
        try:
            if self.image and not self.image_compressed:
                self.image = s3_compress_image(self.image)
        except:
            pass
        # Generate Image Thumbnail
        if self.image and not self.image_thumbnail:
            image_name = str(self.image).split('.')[:-1]
            extension = str(self.image).split('.')[-1]
            image_name = ".".join(image_name)
            image_name = f"{image_name}_thumb.{extension}"
            media_image = Image.open(self.image)
            # copying image to another image object
            media_image.save(f"{settings.MEDIA_ROOT}/{image_name}")
            self.image_thumbnail = image_name
            # Resize image thumbnail to 150 x 150
            thumbnail_picture = Image.open(self.image_thumbnail.path)
            if thumbnail_picture.height > 150 or thumbnail_picture.width > 150:
                # Making it strict to (150, 150) size.
                output_size = (150, 150)
                # We can use resize but to avoid format restrictions, going with thumbnail.
                thumbnail_picture.thumbnail(output_size)
                thumbnail_picture.save(self.image_thumbnail.path, quality=40)
        # Generate Video Thumbnail
        if self.video and not self.video_thumbnail:
            # Get Temporary File Path
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_path = temp_file.name
            with open(temp_path, 'wb+') as destination:
                 for chunk in self.video.chunks():
                           destination.write(chunk)
            # Instantiate VideoFileClip object
            clip = VideoFileClip(temp_path)
            # Get video frame at 1 second
            temp_thumb = clip.get_frame(1)
            # Convert numpy array to pillow image and compress it
            self.video_thumbnail = generate_video_thumbnail(temp_thumb)
        super(ProductMedia, self).save()


    class Meta:
        db_table = "ProductMedia"
        verbose_name_plural = "Product Medias"


class ArchivedProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="archivedproduct_product")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = "ArchivedProduct"
        verbose_name_plural = "Archived Product"

class CollectionProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product = models.ManyToManyField(Product, blank=True, related_name="collectionproduct_product")
    owner = models.ForeignKey(BusinessOwner, on_delete=models.PROTECT, related_name="collectionproduct_owner")

    title = models.CharField(max_length=32, null=True, blank=True, default="")
    description = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
