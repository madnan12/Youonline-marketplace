from django.core.management.base import BaseCommand, CommandError
import json
from classified_app.models import  ClassifiedSubCategory, ClassifiedeMake


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        with open('CSVFiles/classifiedmakes.json', 'r') as f:
            reader = json.load(f)
            # category = AutomotiveCategory.objects.get(title='Cars')
            for i in reader:
                for key, value in i.items():
                    if value:
                        try:
                            sub_category = ClassifiedSubCategory.objects.get(title=key)
                        except:
                            sub_category = ClassifiedSubCategory.objects.create(
                                    title = key
                                )
                        model = ClassifiedeMake.objects.create(
                                subcategory =  sub_category,
                                title = value,
                            )
        self.stdout.write(self.style.SUCCESS(
            'Classified Make added successfully !!'
        ))