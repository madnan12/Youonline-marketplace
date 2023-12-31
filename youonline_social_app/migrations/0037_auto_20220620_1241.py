# Generated by Django 3.2.6 on 2022-06-20 07:41

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0036_profile_blocked_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='blocked_user',
        ),
        migrations.CreateModel(
            name='BlockProfile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('blocked_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blockprofile_blocked_user', to='youonline_social_app.profile')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blockprofile_profile', to='youonline_social_app.profile')),
            ],
            options={
                'db_table': 'BlockProfile',
            },
        ),
    ]
