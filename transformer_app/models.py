# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime, json, logging, os, pprint, subprocess, tempfile
from . import settings_app
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import smart_unicode
from django.utils.text import slugify

log = logging.getLogger(__name__)


class Validator( object ):
    """ Supports view.run_transform_v1() """

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

    # end class Validator


class ViewHelper( object ):
    """ Handles transform code. """

    def handle_get( self, request ):
        return 'foo'

    def build_get_response( self, data ):
        return HttpResponse( 'not yet implemented' )

    def handle_post( self, request ):
        return 'foo'

    def build_post_response( self, data ):
        return HttpResponse( 'not yet implemented' )

    # end class ViewHelper


class Transformer( object ):
    """ Handles transform code. """

    def transform( self, xml_data, xsl_data ):
        """ Manages the transform and returns output. """
        assert type(xml_data) == str
        assert type(xsl_data) == str
        ( temp_xml_path, temp_xsl_path, temp_output_path, transformed_xml ) = ( '', '', '', '' )
        with tempfile.NamedTemporaryFile() as temp_xml:
            temp_xml_path = temp_xml.name
            log.debug( 'temp_xml_path, `%s`' % temp_xml_path )
            log.debug( 'first os.path.exists(temp_xml_path), `%s`' % os.path.exists(temp_xml_path) )
            temp_xml.write( xml_data )
            temp_xml.flush()
            with tempfile.NamedTemporaryFile() as temp_xsl:
                temp_xsl_path = temp_xsl.name
                log.debug( 'temp_xsl_path, `%s`' % temp_xsl_path )
                temp_xsl.write( xsl_data )
                temp_xsl.flush()
                with tempfile.NamedTemporaryFile() as temp_output:
                    temp_output_path = temp_output.name
                    log.debug( 'temp_output_path, `%s`' % temp_output_path )
                    log.debug( 'second os.path.exists(temp_xml_path), `%s`' % os.path.exists(temp_xml_path) )
                    command = 'java -cp %s net.sf.saxon.Transform -t -s:"%s" -xsl:"%s" -o:"%s"' % (
                        settings_app.SAXON_CLASSPATH, temp_xml_path, temp_xsl_path, temp_output_path )
                    log.debug( 'command, `%s`' % command )
                    subprocess.call( [command, '-1'], shell=True )
                    with open( temp_output_path ) as f:
                        transformed_xml = f.read()
                        log.debug( 'transformed_xml, ```%s```' % transformed_xml )
        return transformed_xml

    # def transform( self, xml_data, xsl_data ):
    #     """ Manages the transform and returns output. """
    #     assert type(xml_data) == str
    #     assert type(xsl_data) == str
    #     ( temp_xml_path, temp_xsl_path, temp_output_path, transformed_xml ) = ( '', '', '', '' )
    #     with tempfile.NamedTemporaryFile() as temp_xml:
    #         temp_xml_path = temp_xml.name
    #         log.debug( 'temp_xml_path, `%s`' % temp_xml_path )
    #         log.debug( 'first os.path.exists(temp_xml_path), `%s`' % os.path.exists(temp_xml_path) )
    #         temp_xml.write( xml_data )
    #         temp_xml.flush()
    #     log.debug( 'second os.path.exists(temp_xml_path), `%s`' % os.path.exists(temp_xml_path) )
    #     with tempfile.NamedTemporaryFile() as temp_xsl:
    #         temp_xsl_path = temp_xsl.name
    #         log.debug( 'temp_xsl_path, `%s`' % temp_xsl_path )
    #         temp_xsl.write( xsl_data )
    #         temp_xsl.flush()
    #     with tempfile.NamedTemporaryFile() as temp_output:
    #         temp_output_path = temp_output.name
    #         log.debug( 'temp_output_path, `%s`' % temp_output_path )
    #         command = 'java -cp %s net.sf.saxon.Transform -t -s:"%s" -xsl:"%s" -o:"%s"' % (
    #             settings_app.SAXON_CLASSPATH, temp_xml_path, temp_xsl_path, temp_output_path )
    #         subprocess.call( [command, '-1'], shell=True )
    #         with open( temp_output_path ) as f:
    #             transformed_xml = f.read()
    #             log.debug( 'transformed_xml, ```%s```' % transformed_xml )
    #         temp_output.flush()
    #     return transformed_xml

    # end class Transformer
