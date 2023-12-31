# Generated by Django 3.2.6 on 2022-03-29 08:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('youonline_social_app', '0020_auto_20220322_1457'),
        ('video_app', '0009_auto_20220321_0944'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='videowatched',
            name='post',
        ),
        migrations.AddField(
            model_name='video',
            name='total_views',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='videowatched',
            name='last_watched',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='videowatched',
            name='times_watched',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='videowatched',
            name='video',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='videowatched_video', to='video_app.video'),
        ),
        migrations.AddField(
            model_name='videowatchlater',
            name='video',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='videowatchlater_video', to='video_app.video'),
        ),
        migrations.AlterUniqueTogether(
            name='videowatchlater',
            unique_together={('video', 'profile')},
        ),
        migrations.RemoveField(
            model_name='videowatchlater',
            name='post',
        ),
    ]
