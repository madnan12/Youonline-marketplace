# Generated by Django 3.2.6 on 2022-07-01 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0038_merge_0034_post_product_post_0037_auto_20220620_1241'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='rtl',
            field=models.BooleanField(default=False),
        ),
    ]