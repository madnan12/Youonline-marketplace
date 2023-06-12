

import json

from classified_app.models import ClassifiedCategory , ClassifiedSubCategory
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self , *args, **kwargs):
        with open('CSVFiles/business_directory/business_directory_categories.json' , 'r') as file_:
            read_file = json.load(file_)

            for row in read_file:
                for key, value in row.items():
                    try:
                        category = ClassifiedCategory.objects.get(title = key)
                    except:
                        category = ClassifiedCategory.objects.create(
                            title = key,
                            business_directory = True
                        )
                    for sub_cat in value:
                        try:
                            sub_category =  ClassifiedSubCategory.objects.create(
                                category = category,
                                title = sub_cat['name']
                            )
                        except:
                            pass
            
        self.stdout.write(self.style.SUCCESS(
            'Business Directory categories added successfully !!'
        ))