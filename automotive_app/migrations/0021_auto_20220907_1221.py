# Generated by Django 3.2.6 on 2022-09-07 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automotive_app', '0020_automotivesearchhistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='automotive',
            name='automotive_inspection',
            field=models.CharField(blank=True, choices=[('Courtesy Inspection', 'Courtesy Inspection'), ('Insurance Inspection', 'Insurance Inspection'), ('12Point Inspection', '12 Point Inspection')], max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='automotive',
            name='automotive_year',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='automotive',
            name='fuel_type',
            field=models.CharField(blank=True, choices=[('Petrol', 'Petrol'), ('Diesel', 'Diesel'), ('LPG', 'LPG'), ('CNG & Hybrids', 'CNG & Hybrids'), ('Electric', 'Electric')], max_length=255, null=True),
        ),
    ]