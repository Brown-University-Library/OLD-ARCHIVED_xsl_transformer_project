# -*- coding: utf-8 -*-

from __future__ import unicode_literals
#
import datetime, json, logging, os, pprint, subprocess, tempfile, urllib, urlparse
from xml.etree import ElementTree
#
import requests
from . import settings_app
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import smart_unicode
from django.utils.text import slugify

log = logging.getLogger(__name__)


class Validator( object ):
    """ Validates views.run_transform_v1() input. """

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
        # log.debug( 'request.META, `%s`' % pprint.pformat(request.META) )
        return_val = False
        ( client_ip, auth_key ) = self._get_auth_info( request )
        if auth_key == 'shib' and request.META.get('PATH_INFO', 'unavailable') == '/v1/shib/':
            return_val = True
        elif auth_key == 'whitelist':
            return_val = self._check_whitelist( request.method, request.GET.get('xml_url', 'unavailable'), request.GET.get('xsl_url', 'unavailable') )
        else:
            return_val = self._check_non_shib_info( client_ip, auth_key )
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

    def _check_whitelist( self, method, xml_url, xsl_url ):
        """ Checks xml_url and xsl_url against whitelist.
            Called by check_ip_key() """
        return_val = False
        if method != 'GET' or xml_url == 'unavailable' or xsl_url == 'unavailable':
            return return_val
        ( decoded_xml_url, decoded_xsl_url ) = ( urllib.unquote(xml_url), urllib.unquote(xsl_url) )
        log.debug( 'decoded_xml_url, `%s`; decoded_xsl_url, `%s`' % (decoded_xml_url, decoded_xsl_url) )
        ( xml_hostname, xsl_hostname ) = ( urlparse.urlsplit(decoded_xml_url).hostname, urlparse.urlsplit(decoded_xsl_url).hostname )
        if xml_hostname in settings_app.WHITELISTED_HOSTS and xsl_hostname in settings_app.WHITELISTED_HOSTS:
            return_val = True
        log.debug( 'return_val, `%s`' % return_val )
        return return_val

    def _check_non_shib_info( self, client_ip, auth_key ):
        """ Checks non-shib auth_key against client_ip.
            Called by check_ip_key() """
        return_val = False
        for ( label, dct ) in settings_app.LEGIT_IPS_KEYS.items():
            log.debug( 'label, `%s`; the-dct, `%s`' % (label, dct) )
            if dct['legit_ip'] == client_ip and dct['auth_key'] == auth_key:
                return_val = True
                break
        log.debug( 'return_val, `%s`' % return_val )
        return return_val

    def check_params( self, request ):
        """ Validates params.
            Called by check_validity() """
        return_val = False
        if request.method == 'POST':
            return_val = self._run_param_check( received_params=request.POST.keys(), required_params=['auth_key', 'xml', 'xsl']  )
        elif request.method == 'GET':
            return_val = self._run_param_check( received_params=request.GET.keys(), required_params=['auth_key', 'xml_url', 'xsl_url'] )
        log.debug( 'return_val, `%s`' % return_val )
        return return_val

    def _run_param_check( self, received_params, required_params ):
        """ Validates received-params against required-params.
            Called by check_params() """
        return_val = 'init'
        for required_param in required_params:
            if required_param not in received_params:
                log.debug( 'missing (at least) required_param, `%s`' % required_param )
                return_val = False
                break
        if return_val == 'init':
            return_val = True
        log.debug( 'return_val, `%s`' % return_val )
        return return_val

    # end class Validator


class ViewHelper( object ):
    """ Manages logic-flow for views.run_transform_v1() """

    def __init__( self ):
        self.checker = XMLchecker()

    def handle_get( self, request ):
        """ Calls DataGrabber() and Transformer() to prepare data.
            Called by views.run_transform_v1() """
        ( data_grabber, transformer ) = ( DataGrabber(), Transformer() )
        ( xml_data, xsl_data ) = data_grabber.grab_data( request.GET['xml_url'], request.GET['xsl_url'] )
        transformed_xml = transformer.transform( xml_data, xsl_data )
        return transformed_xml

    def handle_post( self, request ):
        """ Calls Transformer() to prepare data.
            Called by views.run_transform_v1() """
        transformer = Transformer()
        xml_data = request.POST['xml']
        xsl_data = request.POST['xsl']
        transformed_xml = transformer.transform( xml_data, xsl_data )
        return transformed_xml

    def build_response( self, data ):
        """ Builds GET response.
            Content-type info: <http://www.w3.org/TR/xhtml-media-types/>
            Called by views.run_transform_v1() """
        content_type='application/xhtml+xml'
        if self.checker.check_xml( data ) == False:
            content_type='text/text'
        resp = HttpResponse( data, content_type=content_type )
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

    # def execute_transform( self, temp_xml_path, temp_xsl_path, temp_output_file_reference ):
    #     """ Calls saxon and returns the transform result.
    #         Called by transform() """
    #     temp_output_path = temp_output_file_reference.name
    #     log.debug( 'temp_output_path, `%s`' % temp_output_path )
    #     command = 'java -cp %s net.sf.saxon.Transform -t -s:"%s" -xsl:"%s" -o:"%s"' % (
    #         settings_app.SAXON_CLASSPATH, temp_xml_path, temp_xsl_path, temp_output_path )
    #     log.debug( 'command, `%s`' % command )
    #     try:
    #         subprocess.check_output( [command, '-1'], stderr=subprocess.STDOUT, shell=True )
    #         temp_output_file_reference.flush()
    #         transformed_xml = temp_output_file_reference.read().decode('utf-8')  # saxon produces byte-string output
    #     except subprocess.CalledProcessError as e:
    #         log.error( 'exception, ```%s```' % unicode(repr(e)) )
    #         # log.error( 'e.output, `%s`' % e.output )
    #         # log.error( 'e.__dict__, ```%s```' % pprint.pformat(e.__dict__) )
    #         transformed_xml = 'Error on transformation; see log at `%s`' % unicode( datetime.datetime.now() )
    #     log.debug( 'type(transformed_xml), `%s`; transformed_xml, ```%s```' % (type(transformed_xml), transformed_xml) )
    #     return transformed_xml

    # end class Transformer


class XMLchecker( object ):

    def check_xml( self, transformed_output ):
        """ Determines if file is xml-y enough (well-formed). Used to determine correct content-type for response.
            From <http://stackoverflow.com/questions/13742538/how-to-validate-xml-using-python-without-third-party-libs>
            Called by... """
        assert type(transformed_output) == unicode
        return_val = False
        try:
            tree_instance = ElementTree.fromstring( transformed_output.encode('utf-8') )
            return_val = True
        except Exception as e:
            log.debug( 'transformed output must not be xml, ```%s```' % unicode(repr(e)) )
        log.debug( 'return_val, `%s`' % return_val )
        return return_val

    # end class XMLchecker

