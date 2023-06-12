from django.core.management.base import BaseCommand, CommandError
from video_app.models import VideoCategory, VideoSubCategory
import csv

class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        with open('CSVFiles/video_categories.csv', 'r') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                # Skipping the header row
                if i == 0:
                    pass
                else:
                    row = ",".join(row)
                    row = row.split(',')
                    if row[1] == "0":
                        VideoCategory.objects.create(
                                title=row[2]
                            )
                    else:
                        category = VideoCategory.objects.get(title=row[1])
                        VideoSubCategory.objects.create(
                                category=category,
                                title=row[2]
                            )
        self.stdout.write(self.style.SUCCESS(
            'Categories and Sub Categories created Successfully!!'
        ))
