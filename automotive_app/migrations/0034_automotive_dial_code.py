# Generated by Django 3.2.6 on 2022-10-13 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automotive_app', '0033_alter_automotive_fuel_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='automotive',
            name='dial_code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]