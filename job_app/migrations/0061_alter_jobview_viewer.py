# Generated by Django 3.2.6 on 2022-10-04 08:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0047_auto_20220928_1319'),
        ('job_app', '0060_jobview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobview',
            name='viewer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='jobview_viewer', to='youonline_social_app.profile'),
        ),
    ]