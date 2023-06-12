from django.core.management.base import BaseCommand, CommandError
from youonline_social_app.models import ReportProfileCategory


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        # Taking inputs from user
        with open('CSVFiles/report_profile_category.txt') as file:
            for i in file:
                ReportProfileCategory.objects.create(title=i.strip())
        self.stdout.write(self.style.SUCCESS(
            'Report Profile Category added successfully!'
        ))
