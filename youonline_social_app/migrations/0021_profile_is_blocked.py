# Generated by Django 3.2.6 on 2022-03-25 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0020_auto_20220322_1457'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_blocked',
            field=models.BooleanField(default=False),
        ),
    ]