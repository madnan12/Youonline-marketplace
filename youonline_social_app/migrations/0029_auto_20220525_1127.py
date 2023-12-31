# Generated by Django 3.2.6 on 2022-05-25 06:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0031_friendrequest_is_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='alter_mobile',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='skype',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='website',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='userhighschool',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.city'),
        ),
        migrations.AddField(
            model_name='userhighschool',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.country'),
        ),
        migrations.AddField(
            model_name='userhighschool',
            name='graduation_year',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userhighschool',
            name='group',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='userhighschool',
            name='specialization',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='userworkplace',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='userworkplace_country', to='youonline_social_app.country'),
        ),
    ]
