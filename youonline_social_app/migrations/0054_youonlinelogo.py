# Generated by Django 3.2.6 on 2022-11-07 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0053_auto_20221103_1223'),
    ]

    operations = [
        migrations.CreateModel(
            name='YouonlineLogo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.ImageField(blank=True, max_length=255, null=True, upload_to='logo/')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
    ]
