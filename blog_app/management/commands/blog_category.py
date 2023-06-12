
from django.core.management.base import BaseCommand
from ...models import BlogCategory

class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('CSVFiles/blogcategory.txt') as file:
            for i in file:
                BlogCategory.objects.create(title=i)
        print('Blog Category Added')