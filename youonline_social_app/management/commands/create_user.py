from django.core.management.base import BaseCommand, CommandError
import csv
from ...models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        gender='Male'
        user_list=[]
        for i in range (0, 500):
            email=f'adn{i}@gmail.com'
            password=f'Adnanameen{i}@123'
            username=f'username{i}'
            first_name=f'firstname{i}'
            last_name=f'lastname{i}'
            user=User.objects.create(email=email, password=password, username=username, first_name=first_name, last_name=last_name, is_active=True)
            user_list.append(i)
            user.set_password(password)
            user.save()
            profile = Profile.objects.create(
                user=user,
                gender=gender,
            )

            random_digits_for_code = ''.join(
            random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
            verification = VerificationCode.objects.create(code=random_digits_for_code, user=user)

            pp_album = ProfilePictureAlbum.objects.create(
                profile=profile
            )
            profile_picture = ProfilePicture.objects.create(
                album = pp_album
            )
            user_pp = UserProfilePicture.objects.create(
                profile = profile,
                picture = profile_picture
            )
            
            pc_album = ProfileCoverAlbum.objects.create(
                profile=profile
            )
            cover_picture = CoverPicture.objects.create(
                album = pc_album
            )
            user_cp = UserCoverPicture.objects.create(
                profile = profile,
                cover = cover_picture
            )
        print(' Users Created!')