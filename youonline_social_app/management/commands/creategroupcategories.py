from django.core.management.base import BaseCommand, CommandError
from youonline_social_app.models import GroupCategory


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        # Taking inputs from user
        with open('CSVFiles/group_categories.txt') as file:
            for i in file:
                GroupCategory.objects.create(title=i.strip())
        self.stdout.write(self.style.SUCCESS(
            'Group Categories created successfully!'
        ))
