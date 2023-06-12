# Generated by Django 3.2.6 on 2021-12-29 23:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('community_app', '0001_initial'),
        ('youonline_social_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pageinvite',
            name='invited_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pageinvite_invitedby', to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='pageinvite',
            name='page',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pageinvite_page', to='community_app.page'),
        ),
        migrations.AddField(
            model_name='pageinvite',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pageinvite_profile', to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='pagefollower',
            name='page',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pagefollower_page', to='community_app.page'),
        ),
        migrations.AddField(
            model_name='pagefollower',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pagefollower_profile', to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='pagecurrentbanner',
            name='banner',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pagecurrentbanner_banner', to='community_app.pagebanner'),
        ),
        migrations.AddField(
            model_name='pagecurrentbanner',
            name='page',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pagecurrentbanner_page', to='community_app.page'),
        ),
        migrations.AddField(
            model_name='pagecurrentbanner',
            name='uploaded_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pagecurrentbanner_profile', to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='pagebanner',
            name='page',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pagebanner_page', to='community_app.page'),
        ),
        migrations.AddField(
            model_name='pagebanner',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pagebanner_post', to='youonline_social_app.post'),
        ),
        migrations.AddField(
            model_name='pagebanner',
            name='uploaded_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pagebanner_profile', to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='page',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='community_app.groupcategory'),
        ),
        migrations.AddField(
            model_name='page',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='grouprule',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='grouprules_group', to='community_app.group'),
        ),
        migrations.AddField(
            model_name='grouprequest',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='grouprequest_usergroup', to='community_app.group'),
        ),
        migrations.AddField(
            model_name='grouprequest',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='grouprequest_profile', to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='groupmember',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='groupmember_approvedby', to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='groupmember',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='groupmember_usergroup', to='community_app.group'),
        ),
        migrations.AddField(
            model_name='groupmember',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='groupmember_profile', to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='groupinvite',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groupinvite_group', to='community_app.group'),
        ),
        migrations.AddField(
            model_name='groupinvite',
            name='invited_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groupinvite_invitedby', to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='groupinvite',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groupinvite_profile', to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='groupcurrentbanner',
            name='banner',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='groupcurrentbanner_banner', to='community_app.groupbanner'),
        ),
        migrations.AddField(
            model_name='groupcurrentbanner',
            name='group',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='groupcurrentbanner_group', to='community_app.group'),
        ),
        migrations.AddField(
            model_name='groupcurrentbanner',
            name='uploaded_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='groupcurrentbanner_profile', to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='groupbanner',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='groupbanner_group', to='community_app.group'),
        ),
        migrations.AddField(
            model_name='groupbanner',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='groupbanner_post', to='youonline_social_app.post'),
        ),
        migrations.AddField(
            model_name='groupbanner',
            name='uploaded_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='groupbanner_profile', to='youonline_social_app.profile'),
        ),
        migrations.AddField(
            model_name='group',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='community_app.groupcategory'),
        ),
        migrations.AddField(
            model_name='group',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='youonline_social_app.profile'),
        ),
        migrations.AlterUniqueTogether(
            name='pageinvite',
            unique_together={('profile', 'page', 'is_active')},
        ),
        migrations.AlterUniqueTogether(
            name='pagefollower',
            unique_together={('profile', 'page')},
        ),
        migrations.AlterUniqueTogether(
            name='grouprequest',
            unique_together={('profile', 'group', 'status', 'is_active')},
        ),
        migrations.AlterUniqueTogether(
            name='groupmember',
            unique_together={('profile', 'group')},
        ),
        migrations.AlterUniqueTogether(
            name='groupinvite',
            unique_together={('profile', 'group', 'is_active')},
        ),
    ]