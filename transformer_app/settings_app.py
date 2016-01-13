# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json, os


LEGIT_IPS = json.loads( os.environ['XSL__LEGIT_IPS_JSON'] )
LEGIT_GET_KEYS = json.loads( os.environ['XSL__LEGIT_GET_KEYS_JSON'] )
LEGIT_POST_KEYS = json.loads( os.environ['XSL__LEGIT_POST_KEYS_JSON'] )

LEGIT_IPS_KEYS = json.loads( os.environ['XSL_LEGIT_IPS_KEYS_JSON'] )

SAXON_CLASSPATH = os.environ['XSL__SAXON_CLASSPATH']
