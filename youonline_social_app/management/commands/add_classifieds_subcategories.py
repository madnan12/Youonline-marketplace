from django.core.management.base import BaseCommand, CommandError
from classified_app.models import ClassifiedSubCategory
import glob
from django.conf import settings
from django.core.files import File


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        for file in glob.glob(f"{settings.STATIC_ROOT}/youonline_social_app/classified_subcategories/*.png"):
            file_name = file.split('/')[-1]
            title = file_name.split('.')[:-1]
            title = title[0]
            try:
                sub_category = ClassifiedSubCategory.objects.get(title__icontains=title)
                with open(file, 'rb') as f:   # use 'rb' mode for python3
                    data = File(f)
                    sub_category.image.save(f"{title}.png", data, True)
                    self.stdout.write(self.style.SUCCESS(
                        f'Icon added for {sub_category.title}'
                    ))
            except Exception as e:
                self.stdout.write(self.style.SUCCESS(
                    f"{str(e)} - {title}"
                ))
                