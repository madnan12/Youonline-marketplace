from django.core.management.base import BaseCommand, CommandError
import csv
from automotive_app.models import *


def create_make_and_model(category, i, sub_cat):
    try:
        sub_category = AutomotiveSubCategory.objects.get(category=category, title=sub_cat)
    except:
        sub_category = AutomotiveSubCategory.objects.create(
                category = category,
                title = sub_cat
            )
    try:
        make = AutomotiveMake.objects.get(title__icontains=i[2], sub_category=sub_category)
    except:
        make = AutomotiveMake.objects.create(
                title = i[2],
                sub_category = sub_category,
            )
    try:
        model = AutomotiveModel.objects.create(
                brand=make,
                title = i[3],
                year = i[1]
            )
    except Exception as e:
        print(e)


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        with open('CSVFiles/automotive_cars_with_catgegies.csv', 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            try:
                category = AutomotiveCategory.objects.get(title='Cars')
            except:
                category = AutomotiveCategory.objects.create(title='Cars')
            for i in reader:
                sub_cats = str(i[4]).split(',')
                for sub_cat in sub_cats:
                    create_make_and_model(category, i, sub_cat)
        self.stdout.write(self.style.SUCCESS(
            'All Cars Make and Models Added Successfully !!'
        ))
