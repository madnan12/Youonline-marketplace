# Generated by Django 3.2.6 on 2022-01-27 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0007_auto_20220125_1037'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_declined',
            field=models.BooleanField(default=False),
        ),
    ]