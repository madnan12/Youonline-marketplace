# Generated by Django 3.2.6 on 2022-10-13 05:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classified_app', '0026_auto_20221005_1810'),
    ]

    operations = [
        migrations.AddField(
            model_name='classified',
            name='dial_code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
