# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json, os


LEGIT_IPS = json.loads( os.environ['XSL__LEGIT_IPS_JSON'] )
