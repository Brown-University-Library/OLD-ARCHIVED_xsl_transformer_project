import logging
from .models import Transformer, XMLchecker
from django.test import TestCase


log = logging.getLogger(__name__)
TestCase.maxDiff = None


class Transformer_Test( TestCase ):
    """ Tests models.Transformer() """

    def setUp( self ):
        self.tran = Transformer()

    def test__transform( self ):
        """ Tests creation of tmp xml, xsl, and output files. """
        XML_DATA = '''<?xml version="1.0" encoding="UTF-8"?>
        <class>
          <student>Tôm</student>
          <student>Dĭck</student>
          <student>Hârry</student>
        </class>'''
        XSL_DATA = '''<?xml version="1.0" ?>
        <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
          <xsl:template match="student">
            <p><xsl:value-of select="."/></p>
          </xsl:template>
          <xsl:template match="/">
            <html>
            <body>
            <xsl:apply-templates/>
            </body>
            </html>
          </xsl:template>
        </xsl:stylesheet>'''
        transformed_output = self.tran.transform( XML_DATA, XSL_DATA )
        self.assertEqual(
            str,
            type(transformed_output)
            )
        single_line_transformed_output = transformed_output.replace( ' ', '' ).replace( '\n', '' )
        # print single_line_transformed_output
        self.assertEqual(
            '<html><body><p>T\xf4m</p><p>D\u012dck</p><p>H\xe2rry</p></body></html>',  # prints as <html><body><p>Tôm</p><p>Dĭck</p><p>Hârry</p></body></html>
            single_line_transformed_output
            )

    def test_transform_bad( self ):
        """ Tests failed transformation. """
        XML_DATA = '''<student><namez></name></student>'''
        XSL_DATA = '''<?xml version="1.0" ?>
        <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
          <xsl:template match="student">
            <p><xsl:value-of select="."/></p>
          </xsl:template>
          <xsl:template match="/">
            <html>
            <body>
            <xsl:apply-templates/>
            </body>
            </html>
          </xsl:template>
        </xsl:stylesheet>'''
        transformed_output = self.tran.transform( XML_DATA, XSL_DATA )
        self.assertTrue( 'Error on transformation' in transformed_output )

    # end class Transformer_Test


class XMLchecker_Test( TestCase ):
    """ Tests models.XMLchecker() """

    def setUp( self ):
        self.checker = XMLchecker()

    def test_check_non_xml( self ):
        """ Tests well-formedness checker with bad xml. """
        transformed_output = 'foo'
        self.assertEqual(
            False,
            self.checker.check_xml( transformed_output )
            )

    def test_check_good_xml( self ):
        """ Tests well-formedness checker with good xml. """
        transformed_output = '''
            <html>
               <body>

                  <p>Tôm</p>

                  <p>Dĭck</p>

                  <p>Hârry</p>

               </body>
            </html>
            '''
        self.assertEqual(
            True,
            self.checker.check_xml( transformed_output )
            )

    # end class XMLchecker_Test
