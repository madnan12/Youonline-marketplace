# Generated by Django 3.2.6 on 2022-06-13 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0033_post_birthday_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='product_post',
            field=models.BooleanField(default=False),
        ),
    ]
