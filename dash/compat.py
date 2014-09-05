# -*- coding: utf-8 -*-
"""Python 2/3 compatibility module."""


import sys

PY2 = int(sys.version[0]) == 2

if PY2:
    text_type = unicode
    binary_type = str
    string_types = (str, unicode)
    unicode = unicode
    basestring = basestring
else:
    text_type = str
    binary_type = bytes
    string_types = (str,)
    unicode = str
    basestring = (str, bytes)


# Code from http://lucumr.pocoo.org/2011/1/22/forwards-compatible-python/
class UnicodeMixin(object):
    if sys.version_info > (3, 0):
        def __str__(self):
            return self.__unicode__()
    else:
        def __str__(self):
            return unicode(self).encode('utf-8')
