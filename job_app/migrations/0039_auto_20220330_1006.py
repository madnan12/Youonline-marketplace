# Generated by Django 3.2.6 on 2022-03-30 05:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_app', '0038_jobstory_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobprojectmedia',
            name='image',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to='JobProject/images/%Y/%m'),
        ),
        migrations.AlterField(
            model_name='jobprojectmedia',
            name='vid_thumbnail',
            field=models.FileField(max_length=255, null=True, upload_to='JobProject/thumbnail/%Y/%m'),
        ),
        migrations.AlterField(
            model_name='jobprojectmedia',
            name='video',
            field=models.FileField(blank=True, max_length=255, null=True, upload_to='JobProject/videos/%Y/%m'),
        ),
    ]
