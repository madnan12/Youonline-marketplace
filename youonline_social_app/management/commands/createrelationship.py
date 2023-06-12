from django.core.management.base import BaseCommand, CommandError
from youonline_social_app.models import Relationship


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        # Taking inputs from user
        with open('CSVFiles/relationships.txt') as file:
            for i in file:
                Relationship.objects.create(relationship_type=i.strip())
        self.stdout.write(self.style.SUCCESS(
            'Relationships added successfully!'
        ))