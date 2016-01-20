# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json, os


LEGIT_IPS_KEYS = json.loads( os.environ['XSL__LEGIT_IPS_KEYS_JSON'] )

## example XSL__LEGIT_IPS_KEYS_JSON setting (get a random key at `http://127.0.0.1/xsl_transformer/keymaker/`) ##
# export XSL__LEGIT_IPS_KEYS_JSON='
#     {
#       "label_a": {
#         "ip_auth_key": "some_key_a",
#         "legit_ip": "some_ip_a"
#       },
#       "label_b": {
#         "ip_auth_key": "some_key_b",
#         "legit_ip": "some_ip_b"
#       }
#     }
#     '

WHITELISTED_HOSTS = json.loads( os.environ['XSL__WHITELISTED_HOSTS'] )

SAXON_CLASSPATH = os.environ['XSL__SAXON_CLASSPATH']
