# Generated by Django 3.2.6 on 2022-10-05 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property_app', '0021_alter_propertyview_viewer'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='view_count',
            field=models.BigIntegerField(default=0),
        ),
    ]