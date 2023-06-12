from django.core.management.base import BaseCommand, CommandError
from youonline_social_app.models import UserFamilyRelation


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        # Taking inputs from user
        with open('CSVFiles/familyrelations.txt') as file:
            for i in file:
                UserFamilyRelation.objects.create(relationship_name=i.strip())
        self.stdout.write(self.style.SUCCESS(
            'Family Relations added successfully!'
        ))
