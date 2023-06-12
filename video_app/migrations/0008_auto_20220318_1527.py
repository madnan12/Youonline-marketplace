# Generated by Django 3.2.6 on 2022-03-18 10:27

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('video_app', '0007_auto_20220318_1304'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='videoplaylist',
            name='banner',
        ),
        migrations.RemoveField(
            model_name='videoplaylist',
            name='is_compressed',
        ),
        migrations.AlterField(
            model_name='videochannel',
            name='cover',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to='YoutubeCover'),
        ),
        migrations.AlterField(
            model_name='videochannel',
            name='picture',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to='YoutubePicture'),
        ),
        migrations.CreateModel(
            name='PlaylistBanner',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('banner', models.ImageField(blank=True, max_length=255, null=True, upload_to='PlaylistBanners')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('is_compressed', models.BooleanField(default=False)),
                ('bucket_uploaded', models.BooleanField(default=False)),
                ('playlist', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='playlistbanner_playlist', to='video_app.videoplaylist')),
            ],
            options={
                'db_table': 'PlaylistBanner',
            },
        ),
        migrations.CreateModel(
            name='ChannelPicture',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('picture', models.ImageField(blank=True, max_length=255, null=True, upload_to='YoutubePicture')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('is_compressed', models.BooleanField(default=False)),
                ('bucket_uploaded', models.BooleanField(default=False)),
                ('channel', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='channelpicture_channel', to='video_app.videochannel')),
            ],
            options={
                'db_table': 'ChannelPicture',
            },
        ),
        migrations.CreateModel(
            name='ChannelCover',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('cover', models.ImageField(blank=True, max_length=255, null=True, upload_to='YoutubeCover')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('is_compressed', models.BooleanField(default=False)),
                ('bucket_uploaded', models.BooleanField(default=False)),
                ('channel', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='channelcover_channel', to='video_app.videochannel')),
            ],
            options={
                'db_table': 'ChannelCover',
            },
        ),
    ]