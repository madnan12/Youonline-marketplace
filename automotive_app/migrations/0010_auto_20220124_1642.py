# Generated by Django 3.2.6 on 2022-01-24 11:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('automotive_app', '0009_auto_20220118_1237'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='automotivemodel',
            name='category',
        ),
        migrations.AddField(
            model_name='automotivemake',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='automotivemake_subcategory', to='automotive_app.automotivesubcategory'),
        ),
    ]
