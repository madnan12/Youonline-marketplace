# Generated by Django 3.2.6 on 2022-03-16 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property_app', '0005_propertymedia_is_compressed'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertymedia',
            name='video_compressed',
            field=models.BooleanField(default=False),
        ),
    ]
