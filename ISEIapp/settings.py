"""
Django settings for ISEIapp project.

Generated by 'django-admin startproject' using Django 3.2.
For more information on this file, see https://docs.djangoproject.com/en/3.2/topics/settings/
For the full list of settings and their values, see https://docs.djangoproject.com/en/3.2/ref/settings/
"""
from pathlib import Path
from django.core.management.utils import get_random_secret_key
from decouple import config
import sys
import dj_database_url
import os
import environ

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env()

# Base directory is two levels above settings.py (project name: ISEIapp in this case)
BASE_DIR = Path(__file__).resolve().parent.parent

# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ["DEBUG"] =='True'

# DJANGO_ALLOWED_HOSTS for production
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

# Application definition - Add NEW apps here!
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admindocs',

    'users.apps.UsersConfig',

    'teachercert',
    'emailing',
    'reporting',
    'services',
    'apr',
    'accreditation',
     #'selfstudy',
    'selfstudy.apps.SelfstudyConfig',

    'crispy_forms',
    'storages',
    'jquery',
    #'nested_admin',
    #'debug_toolbar',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
]
#if DEBUG:
#    INSTALLED_APPS += ['debug_toolbar']
#    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']


INTERNAL_IPS = [
    '127.0.0.1',
]


ROOT_URLCONF = 'ISEIapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                #makes current school year available in any template {{ current_school_year.name }}
                'ISEIapp.context_processors.current_school_year_processor',
                'ISEIapp.context_processors.navbar_schoolyear_form_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'ISEIapp.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "False") == "True"
if DEVELOPMENT_MODE is True:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.getenv('DATABASE_NAME'),
            'USER': os.getenv('DATABASE_USER'),
            'PASSWORD': os.getenv('DATABASE_PASS'),
            'HOST': os.getenv('DATABASE_HOST',''),
            'PORT': os.getenv('DATABASE_PORT',''),
            'OPTIONS': {'sslmode': 'require'}, #uncomment for digitalocean database
        }
    }
elif len(sys.argv) > 0 and sys.argv[1] != 'collectstatic':
    if os.getenv("DATABASE_URL", None) is None:
        raise Exception("DATABASE_URL environment variable not defined")
    DATABASES = {
        "default": dj_database_url.parse(os.environ.get("DATABASE_URL")),
    }

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/



#AWS_LOCATION = 'static'
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_DEFAULT_ACL = None
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = { 'CacheControl': 'max-age=86400',}
#if DEVELOPMENT_MODE is False:
# s3 static settings
#    STATIC_LOCATION = 'static'
#    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
#    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# s3 media settings
PUBLIC_MEDIA_LOCATION = 'media'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
DEFAULT_FILE_STORAGE = 'ISEIapp.storage_backends.MediaStorage'
#else:
#    MEDIA_URL = '/media/'
#    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# STATIC_LOCATION ='static'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = os.path.join(BASE_DIR, 'static'),


MEDIAFILES_DIRS = [BASE_DIR / "media",]
#STATICFILES_FINDERS = ( 'django.contrib.staticfiles.finders.FileSystemFinder', 'django.contrib.staticfiles.finders.AppDirectoriesFinder',)


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGOUT_REDIRECT_URL = '/login/'

#logout users when they close browser
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

#allow login to inactive users (basically getting a message that their account is inactive)
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.AllowAllUsersModelBackend', )


#print emails to console
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

if DEVELOPMENT_MODE is False:
#print emails to a file
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = '/Users/ritab/Dropbox/B2 IT Development/Web Development/Email testing'
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")

#the gmail setup has to use a two step verifcation the password is an app password (found in Account / Security)
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_USE_TLS = True
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
    EMAIL_PORT = 587

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000  # no of student form fields

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
