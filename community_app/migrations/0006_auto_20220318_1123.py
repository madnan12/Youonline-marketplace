# Generated by Django 3.2.6 on 2022-03-18 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_app', '0005_auto_20220214_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupbanner',
            name='bucket_uploaded',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pagebanner',
            name='bucket_uploaded',
            field=models.BooleanField(default=False),
        ),
    ]