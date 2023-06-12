from .models import Video
import requests
import json

def expire_youtube_link():
    videos = Video.objects.filter(is_deleted=False, inactive_video=False, youtube_link__isnull=False ).order_by('-created_at')[0: 400]
    for v in videos:
        r = requests.get(f"https://www.youtube.com/oembed?format=json&url={v.youtube_link}")
        data = r.text
        if data == 'Bad Request':
            v.inactive_video = True
            v.save()
        else:
            pass
            try:
                data = json.loads(data)
            except Exception as e:
                v.inactive_video = True
                v.save()