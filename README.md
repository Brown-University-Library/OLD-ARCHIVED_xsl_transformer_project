##### overview #####

(UNDER CONSTRUCTION)

[django](https://www.djangoproject.com) application that will run [xslt](https://en.wikipedia.org/wiki/XSLT) (2.0 compatible) transformations, and return the results.


##### security note #####

Run this internally, with trusted xml and xsl files, to avoid xsl security vulnerabilites.

- Tom Eastman's PyCon 2015 talk ["Serialization formats are not toys"](https://www.youtube.com/watch?v=kjZHjvrAS74).
- [OWASP pdf](https://www.owasp.org/images/a/ae/OWASP_Switzerland_Meeting_2015-06-17_XSLT_SSRF_ENG.pdf) on xsl security vulnerabilities.


##### usage #####

You can POST an xsl and xml file, or you can supply GET xsl and xml parameters.

---
