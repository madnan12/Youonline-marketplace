from django.core.management.base import BaseCommand, CommandError
from video_app.models import Video, VideoChannel, VideoPlaylist
from community_app.models import Group, Page
from automotive_app.models import Automotive
from property_app.models import Property
from classified_app.models import Classified
import time as time

class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        try:
            for i in Video.objects.all():
                if not i.slug:
                    slug = i.title.lower().replace(' ', '-')
                    slugs = list(Video.objects.all().values_list('slug', flat=True))
                    if slug in slugs:
                        slug = f"{slug}{time.time()}"
                    i.slug = slug
                    i.save()
            self.stdout.write(self.style.SUCCESS(
                'Video created Slugs successfully!!'
            ))
            for i in VideoChannel.objects.all():
                if not i.slug:
                    slug = i.name.lower().replace(' ', '-')
                    slugs = list(VideoChannel.objects.all().values_list('slug', flat=True))
                    if slug in slugs:
                        slug = f"{slug}{time.time()}"
                    i.slug = slug
                    i.save()      
            self.stdout.write(self.style.SUCCESS(
                'Video Channel Slugs created successfully!!'
            ))
            for i in VideoPlaylist.objects.all():
                if not i.slug:
                    slug = i.name.lower().replace(' ', '-')
                    slugs = list(VideoPlaylist.objects.all().values_list('slug', flat=True))
                    if slug in slugs:
                        slug = f"{slug}{time.time()}"
                    i.slug = slug
                    i.save()
            self.stdout.write(self.style.SUCCESS(
                'Video Playlist Slugs created successfully!!'
            ))
            for i in Group.objects.all():
                if not i.slug:
                    slug = i.name.lower().replace(' ', '-')
                    slugs = list(Group.objects.all().values_list('slug', flat=True))
                    if slug in slugs:
                        slug = f"{slug}{time.time()}"
                    i.slug = slug
                    i.save()
            self.stdout.write(self.style.SUCCESS(
                'Group Slugs created successfully!!'
            ))
            for i in Page.objects.all():
                if not i.slug:
                    slug = i.name.lower().replace(' ', '-')
                    slugs = list(Page.objects.all().values_list('slug', flat=True))
                    if slug in slugs:
                        slug = f"{slug}{time.time()}"
                    i.slug = slug
                    i.save()
            self.stdout.write(self.style.SUCCESS(
                'Page Slugs created successfully!!'
            ))
            for i in Automotive.objects.all():
                if not i.slug:
                    slug = i.name.lower().replace(' ', '-')
                    slugs = list(Automotive.objects.all().values_list('slug', flat=True))
                    if slug in slugs:
                        slug = f"{slug}{time.time()}"
                    i.slug = slug
                    i.save()
            self.stdout.write(self.style.SUCCESS(
                'Automotive Slugs created successfully!!'
            ))
            for i in Property.objects.all():
                if not i.slug:
                    slug = i.name.lower().replace(' ', '-')
                    slugs = list(Property.objects.all().values_list('slug', flat=True))
                    if slug in slugs:
                        slug = f"{slug}{time.time()}"
                    i.slug = slug
                    i.save()
            self.stdout.write(self.style.SUCCESS(
                'Property Slugs created successfully!!'
            ))
            for i in Classified.objects.all():
                if not i.slug:
                    slug = i.name.lower().replace(' ', '-')
                    slugs = list(Classified.objects.all().values_list('slug', flat=True))
                    if slug in slugs:
                        slug = f"{slug}{time.time()}"
                    i.slug = slug
                    i.save()
            self.stdout.write(self.style.SUCCESS(
                'Classified Slugs created successfully!!'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                str(e)
            ))
