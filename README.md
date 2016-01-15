### overview ###

This [django](https://www.djangoproject.com) application runs [xslt](https://en.wikipedia.org/wiki/XSLT) (2.0 compatible) transformations, and returns the results.

Programming languages generally have easy standard ways to apply xslt 1.0 transformations, but may not for xslt 2.0 transformations. This service meets that need.

On this page:

- security note
- usage
- notes


### security note ###

Run this internally, with trusted xml and xsl files, to avoid xsl security vulnerabilites.

- see Tom Eastman's PyCon 2015 talk ["Serialization formats are not toys"](https://www.youtube.com/watch?v=kjZHjvrAS74).
- see [OWASP pdf](https://www.owasp.org/images/a/ae/OWASP_Switzerland_Meeting_2015-06-17_XSLT_SSRF_ENG.pdf) on xsl security vulnerabilities.


### usage ###

You can supply GET xsl and xml urls to web-accessible utf-8 encoded files, or you can POST utf-8 xsl-data and utf-8 xml-data.

- Example GET...

        # -*- coding: utf-8 -*-

        from __future__ import unicode_literals
        import requests

        URL = 'https://host/xsl_transformer/v1/'

        parameters = {
            'xml_url': 'https://url/to/source.xml',
            'xsl_url': 'https://url/to/stylesheet.xsl',
            'auth_key': 'the_auth_key'
            }
        r = requests.get( URL, params=parameters )

- Example POST...

        # -*- coding: utf-8 -*-

        from __future__ import unicode_literals
        import requests

        EXAMPLE_XML = '''<?xml version="1.0" encoding="UTF-8"?>
        <class>
          <student>Tôm</student>
          <student>Dĭck</student>
          <student>Hârry</student>
        </class>'''.encode('utf-8')

        EXAMPLE_XSL = '''<?xml version="1.0" ?>
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
        </xsl:stylesheet>'''.encode('utf-8')

        URL = 'https://host/xsl_transformer/v1/'

        parameters = {
            'xml': EXAMPLE_XML,
            'xsl': EXAMPLE_XSL,
            'auth_key': 'the_auth_key'
            }
        r = requests.post( URL, data=parameters )
        print r.content

        # The output is...
        #
        # <html>
        #    <body>
        #
        #       <p>Tôm</p>
        #
        #       <p>Dĭck</p>
        #
        #       <p>Hârry</p>
        #
        #    </body>
        # </html>


## Notes ##

- an auth_key, for POSTs and GETs, is linked to an IP. For convenience, developers can see their ip, and get a randomly generated key which can be added to the app's settings file, at:

        https://host/xsl_transformer/keymaker/

- for convenience, specified users can test transformation output interactively by using authkey=shib at the url:

        https://host/xsl_transformer/v1/shib/?xml_url=...&xsl_url=...&auth_key=shib


---
