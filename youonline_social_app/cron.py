from . models import *
import datetime

def expire_story():
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    stories = ProfileStory.objects.filter(created_at__lte=yesterday)
    for i in stories:
        i.is_deleted = True
        i.save()

def today_birthday():
    today = datetime.datetime.now()
    profile = Profile.objects.filter(birth_date=today, user__is_active=True, is_deleted=False)
    notification = Notification(
                type = 'Birthday',
                text = 'have his birthday.',
            )
    for i in profile:
        notification.notifiers_list(i)
    notification.save()