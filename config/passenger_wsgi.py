"""
WSGI config for django_template_project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

"""
Prepares application environment.
Variables assume project setup like:
stuff
    django_template_project
        app_x
        config
    env_min_djng
"""

import os, pprint, sys


## become self-aware, padawan
current_directory = os.path.dirname(os.path.abspath(__file__))

## vars
ACTIVATE_FILE = os.path.abspath( u'%s/../../env_min_djng/bin/activate_this.py' % current_directory )
PROJECT_DIR = os.path.abspath( u'%s/../../django_template_project' % current_directory )
PROJECT_ENCLOSING_DIR = os.path.abspath( u'%s/../..' % current_directory )
SETTINGS_MODULE = u'config.settings'
SITE_PACKAGES_DIR = os.path.abspath( u'%s/../../env_min_djng/lib/python2.7/site-packages' % current_directory )

## virtualenv
execfile( ACTIVATE_FILE, dict(__file__=ACTIVATE_FILE) )

## sys.path additions
for entry in [PROJECT_DIR, PROJECT_ENCLOSING_DIR, SITE_PACKAGES_DIR]:
 if entry not in sys.path:
   sys.path.append( entry )

## environment additions
os.environ[u'DJANGO_SETTINGS_MODULE'] = SETTINGS_MODULE  # so django can access its settings

## load up env vars
SETTINGS_FILE = os.environ['DJANGO_TEMPLATE__SETTINGS_PATH']  # set in activate_this.py, and activated above
import shellvars
var_dct = shellvars.get_vars( SETTINGS_FILE )
for ( key, val ) in var_dct.items():
    os.environ[key] = val

## gogogo
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
