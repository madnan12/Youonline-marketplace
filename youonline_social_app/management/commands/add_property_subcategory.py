from django.core.management.base import BaseCommand, CommandError
import json
from property_app.models import SubCategory, Category

class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        with open('CSVFiles/propertysubcategory.json', 'r') as f:
            reader = json.load(f)

            for i in reader:
                for key, value in i.items():
                    if value:
                        try:
                            category = Category.objects.get(title=key)
                        except:
                            category = Category.objects.create(
                                    title = key
                                )
                        model = SubCategory.objects.create(
                                category =  category,
                                title = value,
                            )
        self.stdout.write(self.style.SUCCESS(
            'Property Subcategories added successfully !!'
        ))
        