# Generated by Django 3.2.6 on 2022-09-13 05:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('classified_app', '0018_auto_20220903_1234'),
    ]

    operations = [
        migrations.RenameField(
            model_name='classifiedemake',
            old_name='category',
            new_name='subcategory',
        ),
    ]