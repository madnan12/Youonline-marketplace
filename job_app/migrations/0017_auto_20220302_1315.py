# Generated by Django 3.2.6 on 2022-03-02 08:15

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('job_app', '0016_rename_experience_jobproject_associated_with'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobSearchHistory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('skill', models.CharField(blank=True, max_length=1000, null=True)),
                ('location', models.CharField(blank=True, max_length=1000, null=True)),
                ('employment_type', models.CharField(blank=True, max_length=1000, null=True)),
                ('salary_start_range', models.IntegerField(blank=True, null=True)),
                ('salary_end_range', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'Job Search History',
            },
        ),
        migrations.AlterField(
            model_name='jobprofile',
            name='skill',
            field=models.ManyToManyField(blank=True, to='job_app.Skill'),
        ),
        migrations.CreateModel(
            name='JobAlert',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('location', models.TextField(blank=True, null=True)),
                ('jobprofile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='job_app.jobprofile')),
                ('skill', models.ManyToManyField(blank=True, to='job_app.Skill')),
            ],
            options={
                'db_table': 'Job Alert',
            },
        ),
    ]