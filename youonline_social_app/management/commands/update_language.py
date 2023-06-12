from django.core.management.base import BaseCommand
from ...models import *
import csv


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        langauge = Language.objects.all()
        for l in langauge:
            if l.name =='Arabic' or l.name =='Divehi' or l.name=='Fula' or l.name=='Hebrew (modern)' or l.name=='Kurdish' or l.name=='Persian (Farsi)' or l.name=='Urdu' or l.name=='Azerbaijani':
                l.rtl = True
                l.save()

        self.stdout.write(self.style.SUCCESS(
            'Language Updated Successfully!!'
        ))
