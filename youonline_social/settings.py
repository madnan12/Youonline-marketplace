import os
from pathlib import Path
import environ
from datetime import timedelta
import firebase_admin
from firebase_admin import firestore, initialize_app, credentials


# Initialise environment variables
env = environ.Env()
environ.Env.read_env()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

DOMAIN_NAME = env('DOMAIN_NAME')
FRONTEND_SERVER_NAME = env('FRONTEND_SERVER_NAME')
S3_BUCKET_LINK = env('S3_BUCKET_LINK')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Custom APPs
    'youonline_social_app.apps.YouonlineSocialAppConfig',
    'video_app.apps.VideoAppConfig',
    'community_app.apps.CommunityAppConfig',
    'job_app.apps.JobAppConfig',
    'property_app.apps.PropertyAppConfig',
    'automotive_app.apps.AutomotiveAppConfig',
    'classified_app.apps.ClassifiedAppConfig',
    'chat_app.apps.ChatAppConfig',
    'admin_panel.apps.AdminPanelConfig',
    'blog_app.apps.BlogAppConfig',
    'ecommerce_app.apps.EcommerceAppConfig',
    'rest_framework',
    'rest_framework.authtoken',
    'channels',
    'corsheaders',
    'fcm_django',
    'django_crontab',
    'django.contrib.sitemaps',
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_METHODS = ['*']
CORS_ALLOW_HEADERS = ['*']

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'youonline_social.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'admin_panel.context_processor.admin_profile_picture',
                'youonline_social_app.context_processor.front_end_url',

            ],
            'libraries':{
            'pagination_tags': 'admin_panel.templatetags.pagination_tags',
            
            }
        },
    },
]

# WSGI_APPLICATION = 'youonline_social.wsgi.application'
ASGI_APPLICATION = 'youonline_social.asgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': env('DATABASE_NAME'),
#         'USER': env('DATABASE_USER'),
#         'PASSWORD': env('DATABASE_PASSWORD'),
#         'HOST': env('HOST'),
#         'PORT': '5432',
#         'CONN_MAX_AGE': None,
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# SMTP Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Karachi'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.AllowAny',
    ),
    # Exception Handling
    'NON_FIELD_ERRORS_KEY':'error',
    'EXCEPTION_HANDLER': 
    'youonline_social_app.custom_exceptions.custom_exception_handler',
}

# AWS S3 Configurations
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_SIGNATURE_VERSION = 's3v4'
# AWS_S3_REGION_NAME = 'ap-southeast-1'
AWS_S3_FILE_OVERWRITE = env('AWS_S3_FILE_OVERWRITE')
AWS_DEFAULT_ACL = env('AWS_DEFAULT_ACL')
AWS_S3_VERIFY = env('AWS_S3_VERIFY')
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Custom User Model
AUTH_USER_MODEL = 'youonline_social_app.User'
ADMIN_EMAIL = env('ADMIN_EMAIL')

# Use a service account
cred = credentials.Certificate(os.path.join(BASE_DIR, 'creds/youonline-chat-app-firebase-adminsdk-f215v-dbbd961eea.json'))
firebase_admin.initialize_app(cred)

FIRESTORE = firestore.client()

CRONJOBS = [
    ('* * * * *', 'youonline_social_app.cron.expire_story'),
    ('* * * * *', 'youonline_social_app.cron.today_birthday'),
    ('* * * * *', 'admin_panel.cron.remove_user'),
    ('* * * * *', 'chat_app.cron.unmute_user_chat'),
    ('0 23 * * *', 'video_app.cron.expire_youtube_link'),
]

LOGIN_URL = '/admin_panel_login/'
LOGIN_REDIRECT_URL='/admin_panel_login/'



# Django Channels Settings 

CHANNEL_LAYERS={
    "default" : {
        "BACKEND" : 'channels_redis.core.RedisChannelLayer',
        "CONFIG" : {
            "hosts" : [
                ("localhost" , 6379)
            ]
        }
    }
} 