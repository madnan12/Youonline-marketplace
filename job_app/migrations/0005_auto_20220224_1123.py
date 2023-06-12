# Generated by Django 3.2.6 on 2022-02-24 06:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('job_app', '0004_auto_20220224_1119'),
    ]

    operations = [
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill', models.CharField(max_length=200)),
                ('is_deleted', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'Skill',
            },
        ),
        migrations.AddField(
            model_name='job',
            name='skill',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='job_skill', to='job_app.skill'),
        ),
    ]
