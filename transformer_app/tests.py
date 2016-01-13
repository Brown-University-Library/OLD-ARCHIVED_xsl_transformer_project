# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging
from .models import Transformer
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
            unicode,
            type(transformed_output)
            )
        single_line_transformed_output = transformed_output.replace( ' ', '' ).replace( '\n', '' )
        # print single_line_transformed_output
        self.assertEqual(
            '<html><body><p>T\xf4m</p><p>D\u012dck</p><p>H\xe2rry</p></body></html>',  # prints as <html><body><p>Tôm</p><p>Dĭck</p><p>Hârry</p></body></html>
            single_line_transformed_output
            )

    # end class Transformer_Test
