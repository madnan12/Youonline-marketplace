# Generated by Django 3.2.6 on 2022-03-16 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_app', '0020_auto_20220315_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobprofile',
            name='backgroud_image',
            field=models.ImageField(blank=True, null=True, upload_to='Job Profile/image/%Y/%m'),
        ),
    ]
