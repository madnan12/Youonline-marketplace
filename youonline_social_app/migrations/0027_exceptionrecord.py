# Generated by Django 3.2.6 on 2022-04-25 10:10

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0026_post_business_directory_post'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExceptionRecord',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('content', models.JSONField(default='')),
                ('is_resolved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
    ]
