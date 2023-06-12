# Generated by Django 3.2.6 on 2022-09-03 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automotive_app', '0018_automotivemake_is_featured'),
    ]

    operations = [
        migrations.AddField(
            model_name='automotivecategory',
            name='background_color',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='automotivecategory',
            name='image',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to='automotive_category_images'),
        ),
        migrations.AddField(
            model_name='automotivemake',
            name='background_color',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='automotivemodel',
            name='background_color',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='automotivemodel',
            name='image',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to='automotivemodel_images'),
        ),
        migrations.AddField(
            model_name='automotivesubcategory',
            name='background_color',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='automotivesubcategory',
            name='image',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to='automotive_subcategory_images'),
        ),
        migrations.AddField(
            model_name='automotivesubsubcategory',
            name='background_color',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='automotivesubsubcategory',
            name='image',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to='automotive_subsubcategory_images'),
        ),
    ]
