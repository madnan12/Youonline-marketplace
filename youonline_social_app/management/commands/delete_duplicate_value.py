from django.core.management.base import BaseCommand, CommandError
from automotive_app.models import AutomotiveModel, AutomotiveMake, AutomotiveSubCategory
from classified_app.models import ClassifiedeMake
from youonline_social_app.models import Country
import glob
from django.conf import settings
from django.core.files import File


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        
        automotive_models = AutomotiveModel.objects.all()

        for i in AutomotiveModel.objects.values_list('title', flat=True).distinct():
            AutomotiveModel.objects.filter(pk__in=AutomotiveModel.objects.filter(title=i).values_list('id', flat=True)[1:]).delete()

        for i in AutomotiveMake.objects.values_list('title', flat=True).distinct():
            AutomotiveMake.objects.filter(pk__in=AutomotiveMake.objects.filter(title=i).values_list('id', flat=True)[1:]).delete()

        for c in ClassifiedeMake.objects.values_list('title', flat=True).distinct():
            ClassifiedeMake.objects.filter(pk__in=ClassifiedeMake.objects.filter(title=c).values_list('id', flat=True)[1:]).delete()
        
        for sub in AutomotiveSubCategory.objects.values_list('title', flat=True).distinct():
            AutomotiveSubCategory.objects.filter(pk__in=AutomotiveSubCategory.objects.filter(title=sub).values_list('id', flat=True)[1:]).delete()
        # for c in ClassifiedeMake.objects.values_list('title', flat=True).distinct():
        #     ClassifiedeMake.objects.filter(pk__in=ClassifiedeMake.objects.filter(title=c).values_list('id', flat=True)[1:]).delete()

        for cc in Country.objects.values_list('name', flat=True).distinct():
            Country.objects.filter(pk__in=Country.objects.filter(name=c).values_list('id', flat=True)[1:]).delete()

        self.stdout.write(self.style.SUCCESS(
            'Duplicated Value Removed'
        ))