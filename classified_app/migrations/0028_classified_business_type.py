# Generated by Django 3.2.6 on 2022-10-17 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classified_app', '0027_classified_dial_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='classified',
            name='business_type',
            field=models.CharField(blank=True, choices=[('Individual', 'Individual'), ('Company', 'Company')], max_length=255, null=True),
        ),
    ]
