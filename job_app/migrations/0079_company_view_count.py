# Generated by Django 3.2.6 on 2022-11-01 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_app', '0078_jobapplymedia_file_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='view_count',
            field=models.BigIntegerField(default=0),
        ),
    ]
