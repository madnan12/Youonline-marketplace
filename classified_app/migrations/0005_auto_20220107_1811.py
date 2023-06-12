# Generated by Django 3.2.6 on 2022-01-07 13:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0001_initial'),
        ('classified_app', '0004_alter_classifiedcategory_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favouriteclassified',
            name='classified',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='favouriteclassified_classified', to='classified_app.classified'),
        ),
        migrations.AlterField(
            model_name='favouriteclassified',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='favouriteclassified_profile', to='youonline_social_app.profile'),
        ),
    ]