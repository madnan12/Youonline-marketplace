# Generated by Django 3.2.6 on 2022-02-24 06:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('job_app', '0005_auto_20220224_1123'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='city',
        ),
        migrations.RemoveField(
            model_name='job',
            name='country',
        ),
        migrations.RemoveField(
            model_name='job',
            name='state',
        ),
    ]