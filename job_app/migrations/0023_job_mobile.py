# Generated by Django 3.2.6 on 2022-03-16 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_app', '0022_auto_20220316_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='mobile',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
