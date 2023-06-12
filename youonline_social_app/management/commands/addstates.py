from django.core.management.base import BaseCommand, CommandError
import csv
from ...models import *


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        with open('CSVFiles/states.csv', 'r') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                row = ",".join(row)
                row = row.split(',')
                country = Country.objects.get(counter=row[2])
                State.objects.create(
                    counter=row[0],
                    name=row[1],
                    country=country
                    )
        self.stdout.write(self.style.SUCCESS(
            'States added Successfully!!'
        ))
