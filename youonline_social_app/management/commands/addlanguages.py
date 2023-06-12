from django.core.management.base import BaseCommand, CommandError
import csv
from youonline_social_app.models import *


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        with open('CSVFiles/languages.csv', 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            for i in reader:
                language = Language.objects.create(
                        code = i[1],
                        name = i[2]
                    )
        self.stdout.write(self.style.SUCCESS(
            'Languages Added Successfully !!'
        ))
