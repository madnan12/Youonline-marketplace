# Generated by Django 3.2.6 on 2022-09-26 12:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('job_app', '0053_auto_20220926_1311'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favoritejob',
            name='job',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='favoritejob_job', to='job_app.job'),
        ),
    ]
