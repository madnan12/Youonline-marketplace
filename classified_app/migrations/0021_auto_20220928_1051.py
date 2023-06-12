# Generated by Django 3.2.6 on 2022-09-28 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classified_app', '0020_classified_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classifiedmedia',
            name='classified_image',
            field=models.ImageField(blank=True, max_length=256, null=True, upload_to='classified_images/%Y/%m'),
        ),
        migrations.AlterField(
            model_name='classifiedmedia',
            name='classified_video',
            field=models.FileField(blank=True, max_length=256, null=True, upload_to='classified_video/%Y/%m'),
        ),
        migrations.AlterField(
            model_name='classifiedmedia',
            name='classified_video_thumbnail',
            field=models.FileField(blank=True, max_length=256, null=True, upload_to='classified_video_thumbnail/%Y/%m'),
        ),
    ]
