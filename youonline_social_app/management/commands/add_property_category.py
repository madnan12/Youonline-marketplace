from django.core.management.base import BaseCommand, CommandError
import csv
from property_app.models import Category


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        with open('CSVFiles/property_categories.csv', 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            for i in reader:
                try:
                    category = Category.objects.get(title=i[0])
                except:
                    category = Category.objects.create(title=i[0])    
                
        self.stdout.write(self.style.SUCCESS(
            'Property Category Created Successfully !!'
        ))