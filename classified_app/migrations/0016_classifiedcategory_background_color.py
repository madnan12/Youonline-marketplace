# Generated by Django 3.2.6 on 2022-09-03 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classified_app', '0015_auto_20220902_1106'),
    ]

    operations = [
        migrations.AddField(
            model_name='classifiedcategory',
            name='background_color',
            field=models.TextField(blank=True, null=True),
        ),
    ]