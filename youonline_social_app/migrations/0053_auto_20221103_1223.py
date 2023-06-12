# Generated by Django 3.2.6 on 2022-11-03 07:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classified_app', '0029_auto_20221027_1116'),
        ('automotive_app', '0035_auto_20221027_1116'),
        ('property_app', '0024_auto_20221018_1312'),
        ('job_app', '0079_company_view_count'),
        ('youonline_social_app', '0052_dealdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='automotive',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification_automotive', to='automotive_app.automotive'),
        ),
        migrations.AddField(
            model_name='notification',
            name='classified',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification_classified', to='classified_app.classified'),
        ),
        migrations.AddField(
            model_name='notification',
            name='job',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification_job', to='job_app.job'),
        ),
        migrations.AddField(
            model_name='notification',
            name='property',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification_property', to='property_app.property'),
        ),
    ]
