# Generated by Django 3.2.6 on 2022-10-18 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property_app', '0023_auto_20221005_1810'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='lat',
            field=models.DecimalField(blank=True, decimal_places=16, max_digits=30, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='long',
            field=models.DecimalField(blank=True, decimal_places=16, max_digits=30, null=True),
        ),
    ]