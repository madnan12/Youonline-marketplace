# Generated by Django 3.2.6 on 2022-01-21 07:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0004_auto_20220115_1014'),
    ]

    operations = [
        migrations.AddField(
            model_name='userhighschool',
            name='privacy',
            field=models.CharField(choices=[('Public', 'Public'), ('OnlyMe', 'OnlyMe'), ('Friends', 'Friends')], default='Public', max_length=32),
        ),
        migrations.AddField(
            model_name='userprivacysettings',
            name='street_adress_privacy',
            field=models.CharField(choices=[('Public', 'Public'), ('OnlyMe', 'OnlyMe'), ('Friends', 'Friends')], default='Public', max_length=32),
        ),
        migrations.AddField(
            model_name='useruniversity',
            name='privacy',
            field=models.CharField(choices=[('Public', 'Public'), ('OnlyMe', 'OnlyMe'), ('Friends', 'Friends')], default='Public', max_length=32),
        ),
        migrations.AddField(
            model_name='userworkplace',
            name='privacy',
            field=models.CharField(choices=[('Public', 'Public'), ('OnlyMe', 'OnlyMe'), ('Friends', 'Friends')], default='Public', max_length=32),
        ),
        migrations.AlterField(
            model_name='relationshipstatus',
            name='profile',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile_relationship', to='youonline_social_app.profile'),
        ),
    ]