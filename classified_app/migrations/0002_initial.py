# Generated by Django 3.2.6 on 2021-12-29 23:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('classified_app', '0001_initial'),
        ('job_app', '0001_initial'),
        ('youonline_social_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportclassified',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='favouriteclassified',
            name='classified',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='classified_app.classified'),
        ),
        migrations.AddField(
            model_name='favouriteclassified',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='contactclassified',
            name='classified',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='classified_app.classified'),
        ),
        migrations.AddField(
            model_name='contactclassified',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='classifiedsubsubcategory',
            name='sub_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classified_sub_sub_category', to='classified_app.classifiedsubcategory'),
        ),
        migrations.AddField(
            model_name='classifiedsubcategory',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classified_sub_category', to='classified_app.classifiedcategory'),
        ),
        migrations.AddField(
            model_name='classifiedmedia',
            name='classified',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='classified_app.classified'),
        ),
        migrations.AddField(
            model_name='classifiedmedia',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='classifiedmedia_post', to='youonline_social_app.post'),
        ),
        migrations.AddField(
            model_name='classifiedmedia',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='classified',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='classified_app.classifiedcategory'),
        ),
        migrations.AddField(
            model_name='classified',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.city'),
        ),
        migrations.AddField(
            model_name='classified',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='job_app.company'),
        ),
        migrations.AddField(
            model_name='classified',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.country'),
        ),
        migrations.AddField(
            model_name='classified',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='job_app.currency'),
        ),
        migrations.AddField(
            model_name='classified',
            name='language',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.language'),
        ),
        migrations.AddField(
            model_name='classified',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_classified', to='youonline_social_app.post'),
        ),
        migrations.AddField(
            model_name='classified',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='classified',
            name='state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.state'),
        ),
        migrations.AddField(
            model_name='classified',
            name='sub_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='classified_app.classifiedsubcategory'),
        ),
        migrations.AddField(
            model_name='classified',
            name='sub_sub_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='classified_app.classifiedsubsubcategory'),
        ),
    ]
