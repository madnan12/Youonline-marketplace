# Generated by Django 3.2.6 on 2022-09-27 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0045_auto_20220924_1253'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='dial_code',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]