# Generated by Django 3.2.6 on 2022-06-13 09:51

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('community_app', '0009_page_business_page'),
        ('youonline_social_app', '0034_post_product_post'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessDetails',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=32, null=True)),
                ('description', models.TextField(blank=True, max_length=512, null=True)),
                ('address', models.CharField(blank=True, max_length=128, null=True)),
                ('phone', models.CharField(blank=True, max_length=32, null=True)),
                ('email', models.EmailField(blank=True, max_length=128, null=True)),
                ('checkout_option', models.CharField(choices=[('CashOnDelivery', 'Cash On Delivry'), ('Website', 'Website')], default='CashOnDelivery', max_length=32)),
                ('is_approved', models.BooleanField(default=False)),
                ('website', models.URLField(blank=True, max_length=128, null=True)),
                ('facebook', models.URLField(blank=True, max_length=128, null=True)),
                ('twitter', models.URLField(blank=True, max_length=128, null=True)),
                ('instagram', models.URLField(blank=True, max_length=128, null=True)),
                ('youtube', models.URLField(blank=True, max_length=128, null=True)),
                ('linkedin', models.URLField(blank=True, max_length=128, null=True)),
                ('google', models.URLField(blank=True, max_length=128, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Business Details',
                'db_table': 'BusinessDetails',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(blank=True, max_length=32, null=True)),
                ('description', models.TextField(blank=True, max_length=512, null=True)),
                ('picture', models.ImageField(blank=True, max_length=512, null=True, upload_to='Product')),
                ('brand', models.CharField(blank=True, max_length=128, null=True)),
                ('url', models.URLField(blank=True, max_length=128, null=True)),
                ('color', models.CharField(blank=True, max_length=128, null=True)),
                ('size', models.CharField(blank=True, max_length=128, null=True)),
                ('condition', models.CharField(blank=True, max_length=128, null=True)),
                ('material', models.CharField(blank=True, max_length=128, null=True)),
                ('status', models.BooleanField(default=True)),
                ('quantity', models.IntegerField(default=0)),
                ('availability', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('cost_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('sale_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('business_details', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ecommerce_app.businessdetails')),
            ],
            options={
                'verbose_name_plural': 'Products',
                'db_table': 'Product',
            },
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(max_length=64)),
            ],
            options={
                'verbose_name_plural': 'Product Categories',
                'db_table': 'ProductCategory',
            },
        ),
        migrations.CreateModel(
            name='ProductSubCategory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(max_length=64)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ecommerce_app.productcategory')),
            ],
            options={
                'verbose_name_plural': 'Product Sub Categories',
                'db_table': 'ProductSubCategory',
            },
        ),
        migrations.CreateModel(
            name='ProductMedia',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('image', models.ImageField(blank=True, max_length=512, null=True, upload_to='ProductImages')),
                ('video', models.FileField(blank=True, max_length=512, null=True, upload_to='ProductVideos')),
                ('youtube', models.URLField(blank=True, max_length=128, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ecommerce_app.product')),
            ],
            options={
                'verbose_name_plural': 'Product Medias',
                'db_table': 'ProductMedia',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ecommerce_app.productcategory'),
        ),
        migrations.AddField(
            model_name='product',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='youonline_social_app.post'),
        ),
        migrations.AddField(
            model_name='product',
            name='subcategory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ecommerce_app.productsubcategory'),
        ),
        migrations.CreateModel(
            name='BusinessOwner',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('business_email', models.EmailField(blank=True, max_length=128, null=True)),
                ('full_name', models.CharField(blank=True, max_length=32, null=True)),
                ('profile_picture', models.ImageField(blank=True, max_length=512, null=True, upload_to='BusinessOwnerProfile')),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='youonline_social_app.city')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='youonline_social_app.country')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='youonline_social_app.profile')),
            ],
            options={
                'verbose_name_plural': 'Business Owners',
                'db_table': 'BusinessOwner',
            },
        ),
        migrations.AddField(
            model_name='businessdetails',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ecommerce_app.businessowner'),
        ),
        migrations.AddField(
            model_name='businessdetails',
            name='page',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='community_app.page'),
        ),
    ]
