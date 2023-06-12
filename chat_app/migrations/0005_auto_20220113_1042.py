# Generated by Django 3.2.6 on 2022-01-13 05:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0003_auto_20220110_1717'),
        ('chat_app', '0004_alter_chatmessage_deleted_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='chatmessage_post', to='youonline_social_app.post'),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='post_message',
            field=models.BooleanField(default=False),
        ),
    ]
