# Generated by Django 3.2.6 on 2022-09-30 08:17

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('job_app', '0056_auto_20220930_1259'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='cover_image',
        ),
        migrations.RemoveField(
            model_name='company',
            name='logo',
        ),
        migrations.CreateModel(
            name='CompanyLogo',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('logo', models.ImageField(max_length=256, null=True, upload_to='company/logo/%Y/%m')),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('is_compressed', models.BooleanField(default=False)),
                ('video_compressed', models.BooleanField(default=False)),
                ('bucket_uploaded', models.BooleanField(default=False)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='companylogo_company', to='job_app.company')),
            ],
            options={
                'db_table': 'CompanyLogo',
            },
        ),
        migrations.CreateModel(
            name='CompanyCoverImage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('cover_image', models.ImageField(max_length=256, null=True, upload_to='comapny/cover_image/%Y/%m')),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('is_compressed', models.BooleanField(default=False)),
                ('video_compressed', models.BooleanField(default=False)),
                ('bucket_uploaded', models.BooleanField(default=False)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='companycoverimage_company', to='job_app.company')),
            ],
            options={
                'db_table': 'CompanyCoverImage',
            },
        ),
    ]