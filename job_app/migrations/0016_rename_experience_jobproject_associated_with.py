# Generated by Django 3.2.6 on 2022-02-28 08:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('job_app', '0015_auto_20220228_1253'),
    ]

    operations = [
        migrations.RenameField(
            model_name='jobproject',
            old_name='experience',
            new_name='associated_with',
        ),
    ]
