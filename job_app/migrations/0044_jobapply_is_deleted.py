# Generated by Django 3.2.6 on 2022-04-14 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_app', '0043_alter_jobprojectmedia_vid_thumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobapply',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]