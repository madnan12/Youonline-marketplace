# Generated by Django 3.2.6 on 2022-03-21 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0018_profilestory_is_compressed'),
    ]

    operations = [
        migrations.AddField(
            model_name='userhighschool',
            name='degree',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='userhighschool',
            name='degree_type',
            field=models.CharField(blank=True, choices=[('Intermediate', 'Intermediate'), ('Bachelors', 'Bachelors'), ('Masters', 'Masters'), ('PHD', 'PHD')], max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='userhighschool',
            name='major_subject',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
