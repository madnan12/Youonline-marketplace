# Generated by Django 3.2.6 on 2022-11-18 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property_app', '0025_auto_20221115_1006'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportproperty',
            name='report_type',
            field=models.CharField(blank=True, choices=[('Fraud', 'Fraud'), ('Offensive content', 'Offensive content'), ('Duplicate ad', 'Duplicate ad'), ('Product alread sold', 'Product alread sold'), ('Other', 'Other')], default='Other', max_length=255, null=True),
        ),
    ]
