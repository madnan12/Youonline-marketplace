# Generated by Django 3.2.6 on 2022-01-03 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automotive_app', '0003_auto_20220103_1233'),
    ]

    operations = [
        migrations.AddField(
            model_name='automotivemake',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='automotive_make_images/%Y/%m'),
        ),
    ]