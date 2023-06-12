# Generated by Django 3.2.6 on 2022-02-14 05:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('automotive_app', '0012_automotivemedia_is_compressed'),
    ]

    operations = [
        migrations.CreateModel(
            name='AutomotiveComparison',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('automotive1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='automotivecomparison_automotive1', to='automotive_app.automotive')),
                ('automotive2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='automotivecomparison_automotive2', to='automotive_app.automotive')),
            ],
            options={
                'db_table': 'AutomotiveComparison',
            },
        ),
    ]
