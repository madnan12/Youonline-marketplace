# Generated by Django 3.2.6 on 2022-02-15 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0010_auto_20220214_1027'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='read_by',
            field=models.ManyToManyField(blank=True, related_name='read_notif_profile', to='youonline_social_app.Profile'),
        ),
    ]
