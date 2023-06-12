# Generated by Django 3.2.6 on 2022-09-14 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property_app', '0011_property_property_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='baths',
            field=models.CharField(blank=True, choices=[('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'), ('05', '05'), ('06', '06'), ('07+', '07+')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='property',
            name='bedrooms',
            field=models.CharField(blank=True, choices=[('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'), ('05', '05'), ('06', '06'), ('Studio', 'Studio')], max_length=255, null=True),
        ),
    ]