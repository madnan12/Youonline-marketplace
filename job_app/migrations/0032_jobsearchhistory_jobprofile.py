# Generated by Django 3.2.6 on 2022-03-18 05:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('job_app', '0031_auto_20220317_2337'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobsearchhistory',
            name='jobprofile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='job_app.jobprofile'),
        ),
    ]
