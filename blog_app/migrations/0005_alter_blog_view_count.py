# Generated by Django 3.2.6 on 2022-04-08 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0004_auto_20220321_0944'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='view_count',
            field=models.BigIntegerField(default=0),
        ),
    ]
