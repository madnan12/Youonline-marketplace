# Generated by Django 3.2.6 on 2021-12-29 23:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('job_app', '0001_initial'),
        ('youonline_social_app', '0001_initial'),
        ('automotive_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportautomotive',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='favouriteautomotive',
            name='automotive',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='automotive_app.automotive'),
        ),
        migrations.AddField(
            model_name='favouriteautomotive',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='contactautomotive',
            name='automotive',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='automotive_app.automotive'),
        ),
        migrations.AddField(
            model_name='contactautomotive',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='automotivesubsubcategory',
            name='sub_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='automotive_sub_sub_category', to='automotive_app.automotivesubcategory'),
        ),
        migrations.AddField(
            model_name='automotivesubcategory',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='automotive_sub_category', to='automotive_app.automotivecategory'),
        ),
        migrations.AddField(
            model_name='automotivemodel',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='atuomotivemodel_automotivemake', to='automotive_app.automotivemake'),
        ),
        migrations.AddField(
            model_name='automotivemedia',
            name='automotive',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='automotive_app.automotive'),
        ),
        migrations.AddField(
            model_name='automotivemedia',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='automotivemedia_post', to='youonline_social_app.post'),
        ),
        migrations.AddField(
            model_name='automotivemedia',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='automotive',
            name='automotive_model',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='automotive_atuomotivemodel', to='automotive_app.automotivemodel'),
        ),
        migrations.AddField(
            model_name='automotive',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='automotive_app.automotivecategory'),
        ),
        migrations.AddField(
            model_name='automotive',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.city'),
        ),
        migrations.AddField(
            model_name='automotive',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='job_app.company'),
        ),
        migrations.AddField(
            model_name='automotive',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.country'),
        ),
        migrations.AddField(
            model_name='automotive',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='job_app.currency'),
        ),
        migrations.AddField(
            model_name='automotive',
            name='language',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.language'),
        ),
        migrations.AddField(
            model_name='automotive',
            name='make',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='atuomotive_automotivemake', to='automotive_app.automotivemake'),
        ),
        migrations.AddField(
            model_name='automotive',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_automotive', to='youonline_social_app.post'),
        ),
        migrations.AddField(
            model_name='automotive',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='automotive',
            name='state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.state'),
        ),
        migrations.AddField(
            model_name='automotive',
            name='sub_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='automotive_app.automotivesubcategory'),
        ),
        migrations.AddField(
            model_name='automotive',
            name='sub_sub_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='automotive_app.automotivesubsubcategory'),
        ),
    ]