# Generated by Django 3.2.6 on 2022-02-28 07:43

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0012_post_blog_post'),
        ('job_app', '0013_auto_20220228_1114'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobProject',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('project_url', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('experience', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.userworkplace')),
                ('profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.profile')),
            ],
            options={
                'db_table': 'Job Project',
            },
        ),
    ]
