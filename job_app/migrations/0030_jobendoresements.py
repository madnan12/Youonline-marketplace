# Generated by Django 3.2.6 on 2022-03-17 17:22

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0016_auto_20220316_1236'),
        ('job_app', '0029_auto_20220317_1546'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobEndoresements',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('profile1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='job_app.jobprofile')),
                ('profile2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='youonline_social_app.profile')),
                ('skill', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='job_app.skill')),
            ],
            options={
                'db_table': 'Job Endoresements',
            },
        ),
    ]
