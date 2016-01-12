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
          <student>Tom</student>
          <student>Dick</student>
          <student>Harry</student>
        </class>'''.encode('utf-8')
        XSL_DATA = '''<?xml version="1.0" ?>
        <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
          <xsl:template match="student">
            <p><b><xsl:value-of select="."/></b></p>
          </xsl:template>
          <xsl:template match="/">
            <html>
            <body>
            <xsl:apply-templates/>
            </body>
            </html>
          </xsl:template>
        </xsl:stylesheet>'''.encode('utf-8')
        self.assertEqual(
            'foo',
            self.tran.transform( XML_DATA, XSL_DATA ) )

    # end class Transformer_Test
