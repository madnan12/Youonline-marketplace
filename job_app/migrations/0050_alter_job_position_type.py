# Generated by Django 3.2.6 on 2022-09-13 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_app', '0049_auto_20220913_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='position_type',
            field=models.CharField(blank=True, choices=[('Part Time', 'Part Time'), ('Full Time', 'Full Time'), ('Contract', 'Contract'), ('Temproray', 'Temproray')], max_length=512, null=True),
        ),
    ]
