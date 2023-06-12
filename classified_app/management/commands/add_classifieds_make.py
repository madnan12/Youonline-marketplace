from django.core.management.base import BaseCommand, CommandError
import json
from classified_app.models import ClassifiedCategory, ClassifiedSubCategory


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
                            category = ClassifiedCategory.objects.get(title=key)
                        except:
                            category = ClassifiedCategory.objects.create(
                                    title = key
                                )
                        model = ClassifiedSubCategory.objects.create(
                                category =  category,
                                title = value,
                            )
        self.stdout.write(self.style.SUCCESS(
            'Classified categories added successfully !!'
        ))
        