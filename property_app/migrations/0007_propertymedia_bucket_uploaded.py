# Generated by Django 3.2.6 on 2022-03-17 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property_app', '0006_propertymedia_video_compressed'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertymedia',
            name='bucket_uploaded',
            field=models.BooleanField(default=False),
        ),
    ]