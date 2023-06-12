# Generated by Django 3.2.6 on 2022-06-17 11:18

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0034_profile_last_seen'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportPostCategory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(blank=True, max_length=500, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'ReportPostCategory',
            },
        ),
        migrations.CreateModel(
            name='ReportProfileCategory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(blank=True, max_length=500, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'db_table': 'ReportProfileCategory',
            },
        ),
        migrations.AddField(
            model_name='post',
            name='is_reported',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='is_reported',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='ReportProfile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reportprofile_category', to='youonline_social_app.reportprofilecategory')),
                ('reported_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reportprofile_profile', to='youonline_social_app.profile')),
                ('reported_profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reportprofile_reported_profile', to='youonline_social_app.profile')),
            ],
            options={
                'db_table': 'ReportProfile',
            },
        ),
        migrations.CreateModel(
            name='ReportPost',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reportpost_category', to='youonline_social_app.reportpostcategory')),
                ('post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reportpost_post', to='youonline_social_app.post')),
                ('reported_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reportpost_profile', to='youonline_social_app.profile')),
            ],
            options={
                'db_table': 'ReportPost',
            },
        ),
    ]
