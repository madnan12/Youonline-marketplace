from django.core.management.base import BaseCommand
from ...models import Skill


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('CSVFiles/job_skill.txt') as file:
            for s in file:
                Skill.objects.create(skill=s)
        print('Job Skills Added')