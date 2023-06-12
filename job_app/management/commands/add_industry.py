from django.core.management.base import BaseCommand
from ...models import Industry


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('CSVFiles/add_industry.txt') as file:
            for i in file:
                Industry.objects.create(name=i)
        print('Industry Added')