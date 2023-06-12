from django.core.management.base import BaseCommand, CommandError
import csv
from automotive_app.models import AutomotiveCategory, AutomotiveSubCategory, AutomotiveMake, AutomotiveModel


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        with open('CSVFiles/automotive_categories.csv', 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            for i in reader:
                try:
                    category = AutomotiveCategory.objects.get(title=i[0])
                except:
                    category = AutomotiveCategory.objects.create(title=i[0])    
                try:
                    sub_category = AutomotiveSubCategory.objects.get(
                            category = category,
                            title = i[1]
                        )
                except:
                    sub_category = AutomotiveSubCategory.objects.create(
                            category = category,
                            title = i[1]
                        )
                try:
                    make = AutomotiveMake.objects.get(
                            sub_category = sub_category,
                            title = i[2]
                        )
                except:
                    make = AutomotiveMake.objects.create(
                            sub_category = sub_category,
                            title = i[2]
                        )
                for model in str(i[3]).split(","):
                    AutomotiveModel.objects.create(
                            brand = make,
                            title = model,
                        )
        self.stdout.write(self.style.SUCCESS(
            'Automotive Categories and Sub Categories Created Successfully !!'
        ))