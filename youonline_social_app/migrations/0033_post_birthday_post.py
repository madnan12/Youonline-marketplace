# Generated by Django 3.2.6 on 2022-06-01 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0032_alter_useractivity_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='birthday_post',
            field=models.BooleanField(default=False),
        ),
    ]
