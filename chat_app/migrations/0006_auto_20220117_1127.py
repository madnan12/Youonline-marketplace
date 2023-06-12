# Generated by Django 3.2.6 on 2022-01-17 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat_app', '0005_auto_20220113_1042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatmessagemedia',
            name='audio',
            field=models.FileField(max_length=128, null=True, upload_to='message_audios/%Y/%m'),
        ),
        migrations.AlterField(
            model_name='chatmessagemedia',
            name='image',
            field=models.ImageField(max_length=128, null=True, upload_to='message_images/%Y/%m'),
        ),
        migrations.AlterField(
            model_name='chatmessagemedia',
            name='image_thumbnail',
            field=models.ImageField(max_length=128, null=True, upload_to='message_images/%Y/%m'),
        ),
        migrations.AlterField(
            model_name='chatmessagemedia',
            name='vid_thumbnail',
            field=models.ImageField(max_length=128, null=True, upload_to='message_videos/%Y/%m'),
        ),
        migrations.AlterField(
            model_name='chatmessagemedia',
            name='video',
            field=models.FileField(max_length=128, null=True, upload_to='message_videos/%Y/%m'),
        ),
    ]
