# Generated by Django 3.2.6 on 2022-09-26 08:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0045_auto_20220924_1253'),
        ('job_app', '0052_auto_20220921_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='favoritejob',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='favoritejob_profile', to='youonline_social_app.profile'),
        ),
        migrations.AlterUniqueTogether(
            name='favoritejob',
            unique_together={('profile', 'job')},
        ),
    ]
