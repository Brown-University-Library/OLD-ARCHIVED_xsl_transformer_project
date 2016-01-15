# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime, json, logging, os, pprint, subprocess, tempfile
import requests
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
            GETs with an auth_key of 'shib' require a valid developer shib-login.
            Other GETs, and POSTs, require a valid ip and auth_key.
            Called by views.run_transform_v1() """
        log.debug( 'starting check_validity()' )
        return_val = False
        ( ip_key_check, params_check ) = ( self.check_ip_key(request), self.check_params(request) )
        if ip_key_check == True and params_check == True:
            return_val = True
        log.debug( 'return_val, `%s`' % return_val )
        return return_val

    def check_ip_key( self, request ):
        """ Validates auth_key.
            Called by check_validity() """
        return_val = False
        ( client_ip, auth_key ) = self._get_auth_info( request )
        if auth_key == 'shib':
            return_val = True
        else:
            for ( label, dct ) in settings_app.LEGIT_IPS_KEYS.items():
                if dct['legit_ip'] == client_ip and dct['auth_key'] == auth_key:
                    return_val = True
                    break
        log.debug( 'client_ip, `%s`; auth_key, `%s` has return_val, `%s`' % (client_ip, auth_key, return_val) )
        return return_val

    def _get_auth_info( self, request ):
        """ Grabs client_ip and auth_key.
            Called by check_ip_key() """
        client_ip = request.META.get('REMOTE_ADDR', 'unavailable')
        if request.method == 'GET':
            auth_key = request.GET.get('auth_key', 'unavailable')
        else:
            auth_key = request.POST.get('auth_key', 'unavailable')
        log.debug( '(client_ip, auth_key), ```%s```' % pprint.pformat((client_ip, auth_key)) )
        return ( client_ip, auth_key )

    def check_params( self, request ):
        """ Validates params.
            Called by check_validity() """
        return_val = False
        if request.method == 'POST':
            log.debug( 'sorted(request.POST.keys()), ```%s```' % pprint.pformat(sorted(request.POST.keys())) )
            if sorted( request.POST.keys() ) == [ 'auth_key', 'xml', 'xsl' ]:
                return_val = True
        elif request.method == 'GET':
            log.debug( 'sorted(request.GET.keys()), ```%s```' % pprint.pformat(sorted(request.GET.keys())) )
            if sorted( request.GET.keys() ) == [ 'auth_key', 'xml_url', 'xsl_url' ]:
                return_val = True
        log.debug( 'return_val, `%s`' % return_val )
        return return_val

    # end class Validator


class ViewHelper( object ):
    """ Handles transform code. """

    def handle_get( self, request ):
        """ Calls DataGrabber() and Transformer() to prepare data.
            Called by views.run_transform_v1() """
        ( data_grabber, transformer ) = ( DataGrabber(), Transformer() )
        ( xml_data, xsl_data ) = data_grabber.grab_data( request.GET['xml_url'], request.GET['xsl_url'] )
        transformed_xml = transformer.transform( xml_data, xsl_data )
        return transformed_xml

    def build_get_response( self, data ):
        """ Builds GET response.
            Content-type info: <http://www.w3.org/TR/xhtml-media-types/>
            Called by views.run_transform_v1() """
        resp = HttpResponse( data, content_type='application/xhtml+xml' )
        return resp

    def handle_post( self, request ):
        """ Calls Transformer() to prepare data.
            Called by views.run_transform_v1() """
        transformer = Transformer()
        xml_data = request.POST['xml']
        xsl_data = request.POST['xsl']
        transformed_xml = transformer.transform( xml_data, xsl_data )
        return transformed_xml

    def build_post_response( self, data ):
        """ Builds POST response.
            Called by views.run_transform_v1() """
        resp = HttpResponse( data, content_type='application/xhtml+xml' )
        return resp

    # end class ViewHelper


class DataGrabber( object ):
    """ Grabs GET xml and xsl from urls. """

    def grab_data( self, xml_url, xsl_url ):
        """ Manages getting the xml and xsl data, and returning it in unicode.
            Called by ViewHelper.handle_get() """
        r_xml = requests.get( xml_url )
        xml_data = r_xml.content.decode( 'utf-8' )
        r_xsl = requests.get( xsl_url )
        xsl_data = r_xsl.content.decode( 'utf-8' )
        return ( xml_data, xsl_data )

    # end class DataGrabber


class Transformer( object ):
    """ Handles transform code. """

    def transform( self, xml_data, xsl_data ):
        """ Manages the transform and returns (unicode) output.
            With statements are nested because each temporary file object will disappear once its with-block completes.
            Great tempfile resource: <https://pymotw.com/2/tempfile/>
            Called by ViewHelper.handle_get() & ViewHelper.handle_post() """
        assert type(xml_data) == unicode
        assert type(xsl_data) == unicode
        with tempfile.NamedTemporaryFile() as temp_xml_file_reference:
            temp_xml_path = self.write_xml( temp_xml_file_reference, xml_data )
            with tempfile.NamedTemporaryFile() as temp_xsl_file_reference:
                temp_xsl_path = self.write_xsl( temp_xsl_file_reference, xsl_data )
                with tempfile.NamedTemporaryFile() as temp_output_file_reference:
                    transformed_xml = self.execute_transform( temp_xml_path, temp_xsl_path, temp_output_file_reference )
        return transformed_xml

    def write_xml( self, temp_xml_file_reference, xml_data ):
        """ Writes xml-string to temp object & returns path.
            Called by transform() """
        temp_xml_path = temp_xml_file_reference.name
        log.debug( 'temp_xml_path, `%s`' % temp_xml_path )
        temp_xml_file_reference.write( xml_data.encode('utf-8') )
        temp_xml_file_reference.flush()  # <http://stackoverflow.com/questions/7127075/what-exactly-the-pythons-file-flush-is-doing>
        return temp_xml_path

    def write_xsl( self, temp_xsl_file_reference, xsl_data ):
        """ Writes xsl-string to temp object & returns path.
            Called by transform() """
        temp_xsl_path = temp_xsl_file_reference.name
        log.debug( 'temp_xsl_path, `%s`' % temp_xsl_path )
        temp_xsl_file_reference.write( xsl_data.encode('utf-8') )
        temp_xsl_file_reference.flush()
        return temp_xsl_path

    def execute_transform( self, temp_xml_path, temp_xsl_path, temp_output_file_reference ):
        """ Calls saxon and returns the transform result.
            Called by transform() """
        temp_output_path = temp_output_file_reference.name
        log.debug( 'temp_output_path, `%s`' % temp_output_path )
        command = 'java -cp %s net.sf.saxon.Transform -t -s:"%s" -xsl:"%s" -o:"%s"' % (
            settings_app.SAXON_CLASSPATH, temp_xml_path, temp_xsl_path, temp_output_path )
        log.debug( 'command, `%s`' % command )
        subprocess.call( [command, '-1'], shell=True )
        temp_output_file_reference.flush()
        transformed_xml = temp_output_file_reference.read().decode('utf-8')  # saxon produces byte-string output
        log.debug( 'type(transformed_xml), `%s`; transformed_xml, ```%s```' % (type(transformed_xml), transformed_xml) )
        return transformed_xml

    # def transform( self, xml_data, xsl_data ):
    #     """ Manages the transform and returns output. """
    #     assert type(xml_data) == str
    #     assert type(xsl_data) == str
    #     ( temp_xml_path, temp_xsl_path, temp_output_path, transformed_xml ) = ( '', '', '', '' )
    #     with tempfile.NamedTemporaryFile() as temp_xml:
    #         temp_xml_path = temp_xml.name
    #         log.debug( 'temp_xml_path, `%s`' % temp_xml_path )
    #         temp_xml.write( xml_data )
    #         temp_xml.flush()
    #         with tempfile.NamedTemporaryFile() as temp_xsl:
    #             temp_xsl_path = temp_xsl.name
    #             log.debug( 'temp_xsl_path, `%s`' % temp_xsl_path )
    #             temp_xsl.write( xsl_data )
    #             temp_xsl.flush()
    #             with tempfile.NamedTemporaryFile() as temp_output:
    #                 temp_output_path = temp_output.name
    #                 log.debug( 'temp_output_path, `%s`' % temp_output_path )
    #                 command = 'java -cp %s net.sf.saxon.Transform -t -s:"%s" -xsl:"%s" -o:"%s"' % (
    #                     settings_app.SAXON_CLASSPATH, temp_xml_path, temp_xsl_path, temp_output_path )
    #                 log.debug( 'command, `%s`' % command )
    #                 subprocess.call( [command, '-1'], shell=True )
    #                 with open( temp_output_path ) as f:
    #                     transformed_xml = f.read()
    #                     log.debug( 'transformed_xml, ```%s```' % transformed_xml )
    #     return transformed_xml

    # end class Transformer
