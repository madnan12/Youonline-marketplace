from youonline_social_app.models import *
import datetime

def remove_user():
    Post.objects.create(profile=Profile.objects.first(), text='Cron test')
    current_time = datetime.datetime.now()
    profile = Profile.objects.filter(remove_at__lte=current_time)
    for p in profile:
        p.delete()
        p.user.delete()