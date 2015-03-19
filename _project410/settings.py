"""
Django settings for _project410 project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import dj_database_url


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

#PROJECT_ROOT = os.path.normpath(os.path.join(BASE_DIR, '..'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+ei^7v4d_$7vf+$&cdsrr4zl0$$+c7hxn*ay02vnx+#^snfrp6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = [".herokuapp.com"]


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'rest_framework',
    'main',
    'friends',
    'friendrequest',
)

# Remote Authentication Modifications for Basic HTTP Auth
# https://docs.djangoproject.com/en/dev/howto/auth-remote-user/
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSOR = (
    "django.contrib.auth.context_processors.auth",
    "django.template.context_processors.debug",
    "django.template.context_processors.i18n",
    "django.template.context_processors.media",
    "django.template.context_processors.static",
    "django.template.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)

#AUTHENTICATION_BACKENDS = [
#    'django.contrib.auth.backends.RemoteUserBackend',
#]


ROOT_URLCONF = '_project410.urls'

WSGI_APPLICATION = '_project410.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#          #'NAME': os.path.join(PROJECT_ROOT, 'db.sqlite3'),        
#     }
# }

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Edmonton'

USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'

#if ON_HEROKU:
#   DATABASE_URL = 'postgresql:///postgresql'
#else:
#   DATABASE_URL = 'sqlite://' + os.path.join(BASE_DIR, 'db.sqlite3')
#DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}

#ADDEDEDD THE FOLLLOWWINGGG TO DEAAALLLL WITHTHTHT DB ERRORS WHEN LOCAL

if DEBUG:
     DATABASES = {
         'default': {
         'ENGINE': 'django.db.backends.sqlite3',
         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
         'USER': '',
         'PASSWORD': '',
         'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
         'PORT': '',
     }
 }
# else:
#     DATABASES = {
#         'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'deglt3tqs5mjfa',
#         'HOST': 'ec2-23-21-187-45.compute-1.amazonaws.com',
#         'USER': 'mwmqqmbieymuyq',
#         'PASSWORD' : '3D8Ruktp2PaYUFFvDE-2jKRhaD',
#         'PORT' : '5432',

#     }
# }

#DATABASES = {
#        'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',
#        'NAME': 'deglt3tqs5mjfa',
#        'HOST': 'ec2-23-21-187-45.compute-1.amazonaws.com',
#        'USER': 'mwmqqmbieymuyq',
#        'PASSWORD' : '3D8Ruktp2PaYUFFvDE-2jKRhaD',
#        'PORT' : '5432',

#    }
#}
# Parse database configuration from $DATABASE_URL
#COMMMENTEED OUT THIIIISSS LINNENENENENE
#DATABASES['default'] =  dj_database_url.config()

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SETTINGS_DIR = os.path.dirname(__file__)
PROJECT_PATH = os.path.join(SETTINGS_DIR, os.pardir)
PROJECT_PATH = os.path.abspath(PROJECT_PATH)
TEMPLATE_DIRS = (os.path.join(PROJECT_PATH, '/author/templates'), )
STATIC_ROOT = "/static/images"

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
    '/author/static/images',
)
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_URL = os.path.join(PROJECT_PATH,'/static/')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media') # Absolute path to the media directory

# Restful Framework for Django taken http://www.django-rest-framework.org/
"""REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}"""
