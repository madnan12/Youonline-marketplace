# Generated by Django 3.2.6 on 2022-10-05 13:10

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('automotive_app', '0031_auto_20221005_1810'),
        ('job_app', '0068_auto_20221005_1810'),
        ('property_app', '0023_auto_20221005_1810'),
        ('classified_app', '0026_auto_20221005_1810'),
        ('youonline_social_app', '0047_auto_20220928_1319'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModuleViewHistory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('automotive', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='automotive_app.automotive')),
                ('classified', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='classified_app.classified')),
                ('job', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='job_app.job')),
                ('profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.profile')),
                ('property', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='property_app.property')),
            ],
            options={
                'db_table': 'ModuleViewHistory',
            },
        ),
    ]
