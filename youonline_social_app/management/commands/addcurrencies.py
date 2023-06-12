from django.core.management.base import BaseCommand, CommandError
import csv
from django.core.exceptions import ObjectDoesNotExist
from job_app.models import Currency
from youonline_social_app.models import Country


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        with open('CSVFiles/Currencies.csv', 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            for i in reader:
                Currency.objects.create(
                        name=i[0],
                        code=i[1],
                        currency_symbol=i[2]
                    )
        self.stdout.write(self.style.SUCCESS(
            'Currencies Added Successfully !!'
        ))
