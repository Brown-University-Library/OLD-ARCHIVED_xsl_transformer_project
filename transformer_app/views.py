# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime, json, logging, os, pprint, random
from .models import Validator, ViewHelper
from django.conf import settings as project_settings
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from transformer_app.lib import info_helper


log = logging.getLogger(__name__)
validator = Validator()
view_helper = ViewHelper()


def info( request ):
    """ Returns basic data including branch & commit. """
    log.debug( 'user-agent, ```%s```; ip, ```%s```; referrer, ```%s```' %
        (request.META.get('HTTP_USER_AGENT', None), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_REFERER', None)) )
    rq_now = datetime.datetime.now()
    commit = info_helper.get_commit()
    branch = info_helper.get_branch()
    info_txt = commit.replace( 'commit', branch )
    resp_now = datetime.datetime.now()
    taken = resp_now - rq_now
    context_dct = info_helper.make_context( request, rq_now, info_txt, taken )
    output = json.dumps( context_dct, sort_keys=True, indent=2 )
    return HttpResponse( output, content_type='application/json; charset=utf-8' )


def run_transform_v1( request ):
    """ Manages transform flow. """
    log.debug( 'starting' )
    resp = HttpResponseBadRequest( 'Bad Request' )
    if validator.check_validity( request ) is False:
        return resp
    if request.method == 'GET':
        data = view_helper.handle_get( request )
        resp = view_helper.build_response( data )
    elif request.method == 'POST':
        data = view_helper.handle_post( request )
        resp = view_helper.build_response( data )
    return resp


def keymaker( request ):
    """ Makes keys; convenience for auth-key generation. """
    rndm = random.SystemRandom()
    ALLOWED_CHARACTERS = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789'  # oft-mistaken chars left out
    LENGTH = 50
    key = ''.join( rndm.choice(ALLOWED_CHARACTERS) for i in range(LENGTH) )
    ip = request.META.get('REMOTE_ADDR', 'unavailable')
    output = { 'your_ip': ip, 'random_key': key }
    output = json.dumps( output, sort_keys=True, indent=2 )
    return HttpResponse( output, content_type='application/json; charset=utf-8' )
