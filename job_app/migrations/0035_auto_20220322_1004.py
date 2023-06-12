# Generated by Django 3.2.6 on 2022-03-22 05:04

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('job_app', '0034_auto_20220321_1112'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobproject',
            name='image',
        ),
        migrations.RemoveField(
            model_name='jobproject',
            name='video',
        ),
        migrations.CreateModel(
            name='JobProjectMedia',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='JobProject/images/%Y/%m')),
                ('video', models.FileField(blank=True, null=True, upload_to='JobProject/videos/%Y/%m')),
                ('vid_thumbnail', models.FileField(null=True, upload_to='JobProject/thumbnail/%Y/%m')),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('is_compressed', models.BooleanField(default=False)),
                ('video_compressed', models.BooleanField(default=False)),
                ('jobprofile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='job_app.jobprofile')),
                ('jobproject', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='jobprojectmedia_jobproject', to='job_app.jobproject')),
            ],
            options={
                'db_table': 'Job Project Media',
            },
        ),
    ]
