# Generated by Django 3.2.6 on 2022-03-16 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat_app', '0008_chatmessagemedia_is_compressed'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessagemedia',
            name='video_compressed',
            field=models.BooleanField(default=False),
        ),
    ]
