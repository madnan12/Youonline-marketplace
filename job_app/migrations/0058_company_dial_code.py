# Generated by Django 3.2.6 on 2022-09-30 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_app', '0057_auto_20220930_1317'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='dial_code',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]