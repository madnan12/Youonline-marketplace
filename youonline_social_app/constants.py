import imp
import uuid
from io import BytesIO
from PIL import Image, ImageOps
from django.core.files import File
import re
import sys
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth import get_user_model
from rest_framework.views import exception_handler
import time
import boto3
from django.conf import settings
import random
import string
import subprocess
Image.MAX_IMAGE_PIXELS = 933120000



YOUONLINE_PRIVACY_CHOICES = [
    ('Public', 'Public'),
    ('OnlyMe', 'OnlyMe'),
    ('Friends', 'Friends'),
]

IMAGES_EXTENSIONS = ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG']
VIDEOS_EXTENSIONS = ['mp4', 'mkv', 'webm', 'avi', 'flv', 'wmv', 'mov', 'MP4', 'MKV', 'WEBM', 'AVI', 'FLV', 'WMV', 'MOV']

SUCCESS_RESPONSE_CODE = 200
INTERNAL_SERVER_ERROR_CODE = 500
METHOD_NOT_ALLOWED = 405
UNAUTHORIZED = 401
BAD_REQUEST_CODE = 400
PAGE_NOT_FOUND = 404
PASSWORD = '12345678'

TOKEN_SECURITY_KEY = 'startrekkingacrosstheuniverseonthestarshipenterpriseundercaptainkirk'
TOKEN_ALGORITHM = 'HS256'
EXPIRY_TIME_OF_TOKEN = 15

ADMIN = 1
URL = 'null'
DETAILS = '{}'
STATUS = False

error = "Error"
info = "Info"
failure = "Failure"
success = "Success"
warning = "Warning"



SPAM_CONTENT_LABELS = [
    'Pill', 'Medication', 'Capsule', 'Lingerie', 'Swimwear', 'Bikini', 'Bra', 'Underwear',
    'Apparel', 'Shorts', 'Undershirt', 'Blouse', 'Blonde', 'Thong', 'Panties', 'Hip',
]

SPAM_MODERATED_LABELS = [
    "Explicit Nudity", "Female Swimwear", "Underwear",
    "Female Swimwear Or Underwear", "Graphic Female Nudity", "Revealing Clothes", "Partial Nudity",
    "Drugs", "Pills", "Barechested Male", "Sexual Activity", "Nudity", "Suggestive",
]

SPAM_RESTRICTED_LABELS = [
    "Female Swimwear", "Underwear", "Female Swimwear Or Underwear", "Drugs", "Pills", "Barechested Male", 
    "Rude Gestures", "Middle Finger"
]

female_category = [
    'female',
    'blonde',
    'girl',
    'teen'
]

def check_spam_content(r_labels=[]):
    r_labels = [itm.lower() for itm in r_labels]
    returned_value = None

    def female_spam():
        fct_value = False
        for fct in female_category:
            if fct in r_labels:
                fct_value = True
                break

        return fct_value

    for lb in SPAM_CONTENT_LABELS:
        conditions = [
            True if lb.lower() in r_labels else False,
            True if 'high rise' in r_labels and 'finger' in r_labels else False,
            True if 'spandex' in r_labels and female_spam() else False,
            True if 'pool' in r_labels and female_spam() else False,
            True if 'back' in r_labels and female_spam() else False
        ]

        if any(conditions):
            returned_value = False
            break
        else :
           returned_value = True 
    return returned_value

def is_content_spam(image_name):
    session = boto3.Session(
        aws_access_key_id= settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY,
    )
    client = session.client('rekognition', region_name='ap-southeast-1')
    # for img in all_images:
    image_labels = client.detect_custom_labels(
        Image = {
            'S3Object': {
                'Bucket' : settings.AWS_STORAGE_BUCKET_NAME,
                'Name' : image_name
            },
        },
        MaxLabels=1000,
    )

    all_labels = []
    for i in image_labels['Labels']:
        all_labels.append(i['Name'])
        if len(i['Parents']) > 0:
            for pi in i['Parents']:
                all_labels.append(pi['Name'])

    all_labels = list(set(all_labels))

    return check_spam_content(r_labels=all_labels)

def meta_dictionary(data, success, message, status_code):
    response = {
        'data': data,
        'meta': {
            'success': success,
            'message': message,
            'status_code': status_code,
        }
    }
    return response
    

def s3_compress_image(input_image):
    # Get the image name
    image_name = str(input_image)
    image_name = image_name.split(".")[0]
    # Open Image through Pillow and Compress it
    input_image = Image.open(input_image)

    input_image = ImageOps.exif_transpose(input_image)
    input_image = input_image.convert('RGB')
    img_width = input_image.size[0]
    img_height = input_image.size[1]
    x = img_width / 800
    y = int(img_height // x)
    input_image = input_image.resize((800, y))
    thumb_io = BytesIO()
    input_image.save(thumb_io, format='JPEG', quality=80)
    random_digits_for_image = ''.join(
        random.SystemRandom().choice(string.hexdigits + string.hexdigits) for _ in range(10))
    # Create InMemory File for the image.
    inmemory_uploaded_file = InMemoryUploadedFile(file=thumb_io, field_name=None,
                                                name=f"{image_name}_{random_digits_for_image}.jpeg", content_type='image/jpeg',
                                                size=thumb_io.tell(), charset=None)
    return inmemory_uploaded_file
    

def compress_saved_image(input_image):
    # Get the image name

    image_name = str(input_image)
    extension = image_name.split(".")[-1]
    image_name = image_name.split(".")[0]
    # Open Image through Pillow and Compress it
    input_image = Image.open(input_image)
    input_image = ImageOps.exif_transpose(input_image)
    input_image = input_image.convert('RGB')
    img_width = input_image.size[0]
    img_height = input_image.size[1]
    x = img_width / 800
    y = int(img_height // x)
    input_image = input_image.resize((800, y))
    random_digits_for_image = ''.join(
        random.SystemRandom().choice(string.hexdigits + string.hexdigits) for _ in range(10))
    input_image.save(f"{image_name}_{random_digits_for_image}.jpeg", format='JPEG', quality=80)
    new_image = f"{image_name}_{random_digits_for_image}.jpeg"
    subprocess.call("rm " + image_name + "." + extension, shell=True)
    return new_image


def upload_to_bucket(input_file, output_file):
    session = boto3.Session(
        aws_access_key_id= settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY,
    )
    s3 = session.resource('s3')
    filename = input_file
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    key = output_file
    s3.meta.client.upload_file(Filename=filename, Bucket=bucket, Key=key)


def generate_video_thumbnail(temp_thumb):
    temp_thumb = Image.fromarray(temp_thumb)
    temp_thumb = temp_thumb.convert('RGB')
    img_width = temp_thumb.size[0]
    img_height = temp_thumb.size[1]
    x = img_width / 800
    img_height = int(img_height // x)
    temp_thumb = temp_thumb.resize((800, img_height))
    thumb_io = BytesIO()
    temp_thumb.save(thumb_io, format='JPEG', quality=80)
    random_digits_for_thumbnail = ''.join(
        random.SystemRandom().choice(string.hexdigits + string.hexdigits) for _ in range(10))
    inmemory_uploaded_file = InMemoryUploadedFile(file=thumb_io, field_name=None,
                                                name=f'thumnail_{random_digits_for_thumbnail}.jpeg', content_type='image/jpeg',
                                                size=thumb_io.tell(), charset=None)
    return inmemory_uploaded_file


def password_validator(password):
    return True if re.search(re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!¬#%*?&_()-^=+£/,.])[A-Za-z\d@$!¬#%*?&_()-^=+£/,.]{8,100}$"), password) else False


class EmailOrUsernameModelBackend(object):

    @staticmethod
    def authenticate(username=None, password=None):
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'username': username}
        try:
            user = get_user_model().objects.get(**kwargs)
            if user.check_password(password):
                return user
        # except User.DoesNotExist:
        except:
            return None

    @staticmethod
    def get_user(username):
        try:
            return get_user_model().objects.get(pk=username)
        except get_user_model().DoesNotExist:
            return None


def create_slug(name=None, title=None, slugs=[]):
    non_url_safe = ['"', '#', '$', '%', '&', '+',
                    ',', '/', ':', ';', '=', '?',
                    '@', '[', '\\', ']', '^', '`',
                    '{', '|', '}', '~', "'", '.']
    if name:
        name = name.lower()
        for i in non_url_safe:
            if i in name:
                name = name.replace(i, ' ')
        slug = name.replace(' ', '-')
        slug = slug.replace('--', '-')
        if slug in slugs:
            random_digits_for_slug = ''.join(
                random.SystemRandom().choice(string.hexdigits + string.hexdigits) for _ in range(4))
            slug = f"{slug}-{random_digits_for_slug}"
        return slug
    elif title:
        title = title.lower()
        for i in non_url_safe:
            if i in title:
                title = title.replace(i, ' ')
        slug = title.replace(' ', '-')
        slug = slug.replace('--', '-')
        if slug in slugs:
            random_digits_for_slug = ''.join(
                random.SystemRandom().choice(string.hexdigits + string.hexdigits) for _ in range(4))
            slug = f"{slug}-{random_digits_for_slug}"
        return slug


def generate_page_username(name=None, slugs=[]):
    non_url_safe = ['"', '#', '$', '%', '&', '+',
                    ',', '/', ':', ';', '=', '?',
                    '@', '[', '\\', ']', '^', '`',
                    '{', '|', '}', '~', "'", '.']
    slugs += get_user_model().objects.all().values_list('username' , flat=True)
    if name:
        name = name.lower()
        for i in non_url_safe:
            if i in name:
                name = name.replace(i, ' ')
        slug = name.replace(' ', '')
        slug = slug.replace('--', '')
        if slug in slugs:
            random_digits_for_slug = ''.join(
                random.SystemRandom().choice(string.hexdigits + string.hexdigits) for _ in range(4))
            slug = f"{slug}-{random_digits_for_slug}"
        return slug
    


def youonline_custom_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    print(response)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code
    else:
        response = response

    return response


def check_friendship(profile, visitor_profile):
    request_received = False
    request_sent = False
    is_friend = False
    has_followed = False
    followed_by = False
    try:
        obj = FriendRequest.objects.get(req_sender=profile,
                            req_receiver=visitor_profile,
                            is_active=True,
                            status="Pending"
                    )
        request_received = True
    except:
        pass
    try:
        obj = FriendRequest.objects.get(req_receiver=profile,
                            req_sender=visitor_profile,
                            is_active=True,
                            status="Pending"
                    )
        request_sent = True
    except:
        pass
    try:
        obj = FriendsList.objects.get(profile=visitor_profile)
        if profile in obj.friends.all():
            is_friend = True
    except:
        pass
    try:
        obj = FriendsList.objects.get(profile=visitor_profile)
        if profile in obj.followers.all():
            followed_by = True
    except:
        pass
    try:
        obj = FriendsList.objects.get(profile=visitor_profile)
        if profile in obj.following.all():
            has_followed = True
    except:
        pass

    status_dict = {
        'request_sent': request_sent,
        'request_received': request_received,
        'is_friend': is_friend,
        'has_followed': has_followed,
        'followed_by': followed_by,
    }

    return status_dict

