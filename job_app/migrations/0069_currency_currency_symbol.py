# Generated by Django 3.2.6 on 2022-10-06 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_app', '0068_auto_20221005_1810'),
    ]

    operations = [
        migrations.AddField(
            model_name='currency',
            name='currency_symbol',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
