# -*- coding: utf-8 -*-

from __future__ import unicode_literals
"""
Django settings for django_template_project.

Environmental variables triggered in project's env_min_djng/bin/activate, when using runserver,
  or env_min_djng/bin/activate_this.py, when using apache via passenger.
"""

import json, os
import dj_database_url


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_TEMPLATE__SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
temp_DEBUG = json.loads( os.environ['DJANGO_TEMPLATE__DEBUG_JSON'] )
assert temp_DEBUG in [ True, False ], Exception( 'DEBUG env setting is, "%s"' )
DEBUG = temp_DEBUG

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = json.loads( os.environ['DJANGO_TEMPLATE__ALLOWED_HOSTS'] )  # list


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'transformer_app',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.passenger_wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = json.loads( os.environ['XSL__DATABASES_JSON'] )


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = os.environ['DJANGO_TEMPLATE__STATIC_URL']
STATIC_ROOT = os.environ['DJANGO_TEMPLATE__STATIC_ROOT']  # needed for collectstatic command


# Templates

TEMPLATE_DIRS = json.loads( os.environ['DJANGO_TEMPLATE__TEMPLATE_DIRS'] )  # list


# Email
EMAIL_HOST = os.environ['DJANGO_TEMPLATE__EMAIL_HOST']
EMAIL_PORT = int( os.environ['DJANGO_TEMPLATE__EMAIL_PORT'] )


# sessions

# <https://docs.djangoproject.com/en/1.6/ref/settings/#std:setting-SESSION_SAVE_EVERY_REQUEST>
# Thinking: not that many concurrent users, and no pages where session info isn't required, so overhead is reasonable.
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'logfile': {
            'level':'DEBUG',
            'class':'logging.FileHandler',  # note: configure server to use system's log-rotate to avoid permissions issues
            'filename': os.environ.get(u'DJANGO_TEMPLATE__LOG_PATH'),
            'formatter': 'standard',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'transformer_app': {
            'handlers': ['logfile'],
            'level': os.environ.get(u'DJANGO_TEMPLATE__LOG_LEVEL'),
        },
    }
}

