from django.core.management.base import BaseCommand, CommandError
import csv
from youonline_social_app.models import Country


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        with open('CSVFiles/country_dial_codes.csv', 'r') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                row = ",".join(row)
                row = row.split(',')
                try:
                    country = Country.objects.get(name=row[1])
                    country.dial_code = row[0]
                    country.save()
                except:
                    pass
        self.stdout.write(self.style.SUCCESS(
            row[0]
        ))
