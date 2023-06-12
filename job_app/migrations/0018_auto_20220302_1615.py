# Generated by Django 3.2.6 on 2022-03-02 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_app', '0017_auto_20220302_1315'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='skill',
        ),
        migrations.AddField(
            model_name='job',
            name='skill',
            field=models.ManyToManyField(blank=True, related_name='job_skill', to='job_app.Skill'),
        ),
    ]
