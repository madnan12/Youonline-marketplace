# Generated by Django 3.2.6 on 2022-09-02 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classified_app', '0014_auto_20220830_1105'),
    ]

    operations = [
        migrations.AddField(
            model_name='classifiedsubcategory',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='classifiedsubcategory',
            name='image',
            field=models.ImageField(max_length=255, null=True, upload_to='classified_subcategory_images'),
        ),
    ]