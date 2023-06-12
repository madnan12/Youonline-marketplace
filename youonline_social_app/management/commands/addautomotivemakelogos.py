from django.core.management.base import BaseCommand, CommandError
from automotive_app.models import *
from media import automotive_make_images
import os
from youonline_social import settings
from PIL import Image
class Command(BaseCommand):
	# Handle method to handle out the process of adding logos to the automotive make
	def handle(self, *args, **options):
		makes = AutomotiveMake.objects.all()
		for i in makes:
			try:
				Image.open(os.path.join(settings.MEDIA_ROOT + '/automotive_make_images/' + str(i.title) + '.png'))
				i.image = 'automotive_make_images/' + str(i.title) + '.png'
				i.save()
			except Exception as e:
				pass
				# print(str(e))
		self.stdout.write(self.style.SUCCESS(
			'Logos Added to AutomotiveMake successfully !!!'
		))