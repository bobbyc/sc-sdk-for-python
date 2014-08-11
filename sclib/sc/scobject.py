# Copyright (c) 2012 Trend Micro, Inc. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

"Handle SecureCloud basic connection to SC Management API"

from xml.etree import ElementTree
from xml.dom.minidom import parseString


class SCObject(object):
    # Base class of All SecureCloud objects

    #
    # member functions
    #
    def __init__(self, connection=None, tag=''):
        self.connection = connection
        self.__tag = tag

    @property
    def tag(self):
        return self.__tag

    def startElement(self, name, attrs, connection):
        # Mostly parsing XML attributes and begin of elements
        return None

    def endElement(self, name, value, connection):
        # Mostly parsing XML elements
        setattr(self, name, value)

    def buildElements(self):
        #
        # To build xml elements structure
        #
        pass

    def tostring(self):
        return ElementTree.tostring(self.buildElements(), encoding='utf-8')

    def niceFormat(self):
        # build from self's elements
        xmlstr = parseString(self.tostring())
        pretty_res = xmlstr.toprettyxml()
        return pretty_res
