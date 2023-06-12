from django.core.management.base import BaseCommand, CommandError
from youonline_social_app.models import ReportPostCategory


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        # Taking inputs from user
        with open('CSVFiles/report_post_category.txt') as file:
            for i in file:
                ReportPostCategory.objects.create(title=i.strip())
        self.stdout.write(self.style.SUCCESS(
            'Report Post Category added successfully!'
        ))
