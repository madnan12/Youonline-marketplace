# Generated by Django 3.2.6 on 2022-09-03 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classified_app', '0016_classifiedcategory_background_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='classifiedemake',
            name='background_color',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='classifiedsubcategory',
            name='background_color',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='classifiedsubsubcategory',
            name='background_color',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='classifiedsubsubcategory',
            name='image',
            field=models.ImageField(blank=True, max_length=256, null=True, upload_to='classified_subsub_images'),
        ),
    ]
