# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime, json, logging, os, pprint, random
from django.conf import settings as project_settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from .models import Validator, ViewHelper
from django.shortcuts import get_object_or_404, render

log = logging.getLogger(__name__)
validator = Validator()
view_helper = ViewHelper()


def hi( request ):
    """ Returns simplest response. """
    now = datetime.datetime.now()
    return HttpResponse( '<p>hi</p> <p>( %s )</p>' % now )


def run_transform_v1 ( request ):
    """ Manages transform flow. """
    log.debug( 'starting' )
    resp = HttpResponseBadRequest( 'Bad Request' )
    if validator.check_validity( request ) is False:
        return resp
    if request.method == 'GET':
        data = view_helper.handle_get( request )
        resp = view_helper.build_get_response( data )
    elif request.method == 'POST':
        data = view_helper.handle_post( request )
        resp = view_helper.build_post_response( data )
    return resp


def keymaker( request ):
    """ Makes keys; convenience for auth-key generation. """
    rndm = random.SystemRandom()
    ALLOWED_CHARACTERS = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789'  # oft-mistaken chars left out
    LENGTH = 50
    key = ''.join( rndm.choice(ALLOWED_CHARACTERS) for i in range(LENGTH) )
    return HttpResponse( key, content_type='text/text' )
