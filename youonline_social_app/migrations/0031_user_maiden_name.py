# Generated by Django 3.2.6 on 2022-05-27 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0030_useractivity'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='maiden_name',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]