# Generated by Django 3.2.6 on 2022-03-17 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_app', '0028_job_job_duration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='experience',
        ),
        migrations.AddField(
            model_name='job',
            name='education',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='max_experience',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='min_experience',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]