from django.core.management.base import BaseCommand, CommandError
import csv
from automotive_app.models import *


class Command(BaseCommand):
	# Handle method to handle out the process of creating the admin user
	def handle(self, *args, **options):
		makes = AutomotiveMake.objects.distinct('title')
		for i in makes:
			for j in AutomotiveModel.objects.filter(brand__title=i.title):
				j.brand = i
				j.save()

		for i in AutomotiveMake.objects.all():
			models = AutomotiveModel.objects.filter(brand=i)
			if models.count() < 1:
				i.delete()


		unq_models = list(AutomotiveModel.objects.distinct('brand', 'title').values_list('id', flat=True))
		for i in AutomotiveModel.objects.all():
			if i.id not in unq_models:
				i.delete()
		self.stdout.write(self.style.SUCCESS(
			'Record made unique successfully !!'
		))