from django.core.management.base import BaseCommand, CommandError
import json
from ecommerce_app.models import ProductCategory, ProductSubCategory


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        with open('CSVFiles/classifiedcategories.json', 'r') as f:
            reader = json.load(f)
            # category = AutomotiveCategory.objects.get(title='Cars')
            for i in reader:
                for key, value in i.items():
                    if value:
                        try:
                            category = ProductCategory.objects.get(title=key)
                        except:
                            category = ProductCategory.objects.create(
                                    title = key
                                )
                        model = ProductSubCategory.objects.create(
                                category = category,
                                title = value,
                            )
        self.stdout.write(self.style.SUCCESS(
            'Product categories added successfully !!'
        ))