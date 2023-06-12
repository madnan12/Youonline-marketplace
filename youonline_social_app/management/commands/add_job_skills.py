from unicodedata import name
from django.core.management.base import BaseCommand, CommandError
from job_app.models import Skill
import json

class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        with open('CSVFiles/job_skill.json', 'r') as f:
            file_data = json.load(f)
            for i in file_data:
                try:
                    Skill.objects.get(
                        skill=i
                    )
                except:
                    Skill.objects.create(
                        skill=i
                    )

        self.stdout.write(self.style.SUCCESS(
            'Industries added Successfully!!'
        ))
