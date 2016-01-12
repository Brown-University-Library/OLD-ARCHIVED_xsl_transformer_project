# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime, json, logging, os, pprint, itertools
from . import settings_app
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.encoding import smart_unicode
from django.utils.text import slugify

log = logging.getLogger(__name__)


class HelperV1( object ):

    def check_validity( self, request ):
        """ Checks ip & params.
            Called by views.run_transform_v1() """
        log.debug( 'starting check_validity()' )
        return_val = False
        if self.check_ip( unicode(request.META.get('REMOTE_ADDR', 'unavailable')) ) == True and self.check_params( request ) == True:
            return_val = True
        log.debug( 'return_val, `%s`' % return_val )
        return return_val

    def check_ip( self, client_ip ):
        """ Validates ip.
            Called by check_validity() """
        return_val = False
        if client_ip in settings_app.LEGIT_IPS:
            return_val = True
        else:
            log.warning( 'bad ip, `%s`' % client_ip )
            return_val = False
        log.debug( 'ip, `%s` has return_val, `%s`' % (client_ip, return_val) )
        return return_val

    def check_params( self, request ):
        """ Validates params.
            Called by check_validity() """
        return_val = False
        if request.method == 'POST':
            log.debug( 'sorted(request.POST.keys()), ```%s```' % pprint.pformat(sorted(request.POST.keys())) )
            if sorted( request.POST.keys() ) == settings_app.LEGIT_POST_KEYS:
                return_val = True
        elif request.method == 'GET':
            log.debug( 'sorted(request.GET.keys()), ```%s```' % pprint.pformat(sorted(request.GET.keys())) )
            if sorted( request.GET.keys() ) == settings_app.LEGIT_GET_KEYS:
                return_val = True
        log.debug( 'return_val, `%s`' % return_val )
        return return_val
