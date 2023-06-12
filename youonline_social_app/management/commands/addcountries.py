from django.core.management.base import BaseCommand, CommandError
from ...models import *
import csv


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        with open('CSVFiles/countries2.csv', 'r') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                row = ",".join(row)
                row = row.split(',')
                Country.objects.create(
                    counter=row[0],
                    country_code=row[1],
                    name=row[2]
                    )
        self.stdout.write(self.style.SUCCESS(
            'Countries added Successfully!!'
        ))
