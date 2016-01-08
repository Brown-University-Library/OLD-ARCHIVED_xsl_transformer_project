# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime, json, logging, os, pprint, itertools
from django.conf import settings as project_settings
from django.core.urlresolvers import reverse
from django.db import models
from django.http import HttpResponseRedirect
from django.utils.encoding import smart_unicode
from django.utils.text import slugify

log = logging.getLogger(__name__)

