# Generated by Django 3.2.6 on 2022-03-16 10:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('job_app', '0021_jobprofile_backgroud_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='favoritejob',
            name='profile',
        ),
        migrations.AddField(
            model_name='favoritejob',
            name='jobprofile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='job_app.jobprofile'),
        ),
    ]
