from django.core.management.base import BaseCommand, CommandError
import csv
from ...models import *


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        with open('CSVFiles/cities.csv', 'r') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                row = ",".join(row)
                row = row.split(',')
                state = State.objects.get(counter=row[2])
                City.objects.create(
                    counter=row[0],
                    name=row[1],
                    state=state
                    )
        self.stdout.write(self.style.SUCCESS(
            'Cities added Successfully!!'
        ))
