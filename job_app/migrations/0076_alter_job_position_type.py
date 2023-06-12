# Generated by Django 3.2.6 on 2022-10-21 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_app', '0075_jobapply_dial_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='position_type',
            field=models.CharField(blank=True, choices=[('Part Time', 'Part Time'), ('Full Time', 'Full Time'), ('Contract', 'Contract'), ('Temporary', 'Temporary')], max_length=512, null=True),
        ),
    ]