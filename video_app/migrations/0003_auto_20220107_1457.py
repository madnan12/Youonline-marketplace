# Generated by Django 3.2.6 on 2022-01-07 09:57

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0001_initial'),
        ('video_app', '0002_auto_20220106_1757'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoChannelSubscribe',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('channel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='videochannelsubscribe_channel', to='video_app.videochannel')),
                ('profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='videochannelsubscribe_profile', to='youonline_social_app.profile')),
            ],
            options={
                'db_table': 'VideoChannelSubscribe',
                'unique_together': {('profile', 'channel')},
            },
        ),
        migrations.DeleteModel(
            name='VideoSubscribe',
        ),
    ]
