# Generated by Django 3.2.6 on 2022-01-14 06:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0003_auto_20220110_1717'),
        ('classified_app', '0005_auto_20220107_1811'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='favouriteclassified',
            unique_together={('profile', 'classified')},
        ),
    ]
