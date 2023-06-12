# Generated by Django 3.2.6 on 2022-09-21 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property_app', '0012_auto_20220914_1742'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='business_type',
            field=models.CharField(blank=True, choices=[('Individual', 'Individual'), ('Company', 'Company')], max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='company_license',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='company_name',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
