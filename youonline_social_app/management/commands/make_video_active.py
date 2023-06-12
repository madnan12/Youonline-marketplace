from django.core.management.base import BaseCommand
from video_app.models import Video
import requests
import json
    



class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        videos = Video.objects.filter(is_deleted=False, youtube_link__isnull=False )
        for v in videos:
            v.inactive_video = False
            v.save()
        self.stdout.write(self.style.SUCCESS(
            'Video Now Active!!'
        ))
