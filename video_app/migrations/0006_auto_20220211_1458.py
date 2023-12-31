# Generated by Django 3.2.6 on 2022-02-11 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video_app', '0005_alter_video_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='videochannel',
            name='is_compressed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='videoplaylist',
            name='is_compressed',
            field=models.BooleanField(default=False),
        ),
    ]
