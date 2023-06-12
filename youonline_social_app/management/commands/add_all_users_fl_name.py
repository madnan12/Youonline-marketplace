

from youonline_social_app.models import User

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        all_users = User.objects.filter(is_active=True)

        for usr in all_users:
            full_name = f'{usr.first_name} {usr.last_name}'
            usr.name = full_name
            usr.save()