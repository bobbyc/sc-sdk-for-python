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

from sclib.sc.scobject import SCObject
from xml.etree import ElementTree


class DSMConnSettings(SCObject):

    ValidAttributes = ['Enabled', 'ServerAddress', 'Port',
                       'Tenant', 'Username', 'Password']

    def __init__(self, connection):
        SCObject.__init__(self, connection)
        self.Enabled = None
        self.ServerAddress = None
        self.Port = None
        self.Tenant = None
        self.Username = None
        self.Password = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret

        if name == 'DSMConnSettings':
            for key, value in attrs.items():
                if key in self.ValidAttributes:
                    setattr(self, key, value)
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'Enabled':
            self.Enabled = value
        elif name == 'ServerAddress':
            self.ServerAddress = value
        elif name == 'Port':
            self.Port = value
        elif name == 'Tenant':
            self.Tenant = value
        elif name == 'Username':
            self.Username = value
        elif name == 'Password':
            self.Password = value

    def buildElements(self):
        setting = ElementTree.Element('DSMConnSettings')

        # Set all valid Elements
        if self.Enabled:
            ElementTree.SubElement(setting, "Enabled").text = self.Enabled
        if self.ServerAddress:
            ElementTree.SubElement(
                setting, "ServerAddress").text = self.ServerAddress
        if self.ServerAddress:
            ElementTree.SubElement(setting, "Port").text = self.Port
        if self.ServerAddress:
            ElementTree.SubElement(setting, "Tenant").text = self.Tenant
        if self.ServerAddress:
            ElementTree.SubElement(setting, "Username").text = self.Username
        if self.ServerAddress:
            ElementTree.SubElement(setting, "Password").text = self.Password

        return setting

    def update(self):
        action = '%s/' % (self.connection.REST_DSM_SETTING)
        data = self.tostring()
        response = self.connection.get_status(action, data=data, method='POST')
        return response
    

class KMIPConnSettings(SCObject):

    ValidAttributes = ['accountDBID', 'active',
                       'canModify', 'clientCertPassword',
                       'doTestConnection', 'enabled',
                       'hostname', 'id', 'port']

    def __init__(self, connection):
        SCObject.__init__(self, connection)

        # attributes
        self.accountDBID = None
        self.active = None
        self.canModify = None
        self.clientCertPassword = None
        self.doTestConnection = None
        self.enabled = None
        self.hostname = None
        self.id = None
        self.port = None

        # elements
        self.clientCertificateFileName = None
        self.clientCertificate = None
        self.clientPrivateKeyFileName = None
        self.clientPrivateKey = None
        self.serverCertificateFileName = None
        self.serverCertificate = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret

        if name == 'kmipConnectionSetting':
            for key, value in attrs.items():
                if key in self.ValidAttributes:
                    setattr(self, key, value)
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'clientCertificateFileName':
            self.clientCertificateFileName = value
        elif name == 'clientCertificate':
            self.clientCertificate = value
        elif name == 'clientPrivateKeyFileName':
            self.clientPrivateKeyFileName = value
        elif name == 'clientPrivateKey':
            self.clientPrivateKey = value
        elif name == 'serverCertificateFileName':
            self.serverCertificateFileName = value
        elif name == 'serverCertificate':
            self.serverCertificate = value

    def buildElements(self):
        setting = ElementTree.Element('kmipConnectionSetting')

        # build attributes
        for e in self.ValidAttributes:
            if getattr(self, e):
                setting.attrib[e] = getattr(self, e)

        # Set all valid Elements
        if self.Enabled:
            ElementTree.SubElement(
                setting, "clientCertificateFileName").text = self.clientCertificateFileName
        if self.ServerAddress:
            ElementTree.SubElement(
                setting, "clientCertificate").text = self.clientCertificate
        if self.ServerAddress:
            ElementTree.SubElement(
                setting, "clientPrivateKeyFileName").text = self.clientPrivateKeyFileName
        if self.ServerAddress:
            ElementTree.SubElement(
                setting, "clientPrivateKey").text = self.clientPrivateKey
        if self.ServerAddress:
            ElementTree.SubElement(
                setting, "serverCertificateFileName").text = self.serverCertificateFileName
        if self.ServerAddress:
            ElementTree.SubElement(
                setting, "serverCertificate").text = self.serverCertificate

        return setting


class Language(SCObject):
    ValidAttributes = ['isDefault', 'languageCode']

    def __init__(self, connection):
        SCObject.__init__(self, connection)

        # attributes
        self.isDefault = None
        self.languageCode = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret

        if name == 'language':
            for key, value in attrs.items():
                setattr(self, key, value)
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)

    def buildElements(self):
        language = ElementTree.Element('language')

        # build attributes
        for e in self.ValidAttributes:
            if getattr(self, e):
                language.attrib[e] = getattr(self, e)

        return language


class Timezone(SCObject):
    ValidAttributes = ['baseUtcOffset', 'timezonEn', 'timezoneId']

    def __init__(self, connection):
        SCObject.__init__(self, connection)

        # attributes
        self.baseUtcOffset = None
        self.timezonEn = None
        self.timezoneId = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret

        if name == 'timezone':
            for key, value in attrs.items():
                if key in self.ValidAttributes:
                    setattr(self, key, value)
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)

    def buildElements(self):
        timezone = ElementTree.Element('timezone')

        # build attributes
        for e in self.ValidAttributes:
            if getattr(self, e):
                setting.attrib[e] = getattr(self, e)

        return timezone


class License(SCObject):
    ValidAttributes = ['ac', 'account', 'activationDate', 'expirationDate', 'expireNotificationDate',
                       'gracePeriod', 'id', 'inUse', 'isPRLicense', 'isTrial', 'lastUpdate', 'seats',
                       'updateInterval', 'verifyStatus', 'LicenseProfile']

    def __init__(self, connection):
        SCObject.__init__(self, connection)

        # attributes
        self.ac = None
        self.account = None
        self.activationDate = None
        self.expirationDate = None
        self.expireNotificationDate = None
        self.gracePeriod = None
        self.id = None
        self.inUse = None
        self.isPRLicense = None
        self.isTrial = None
        self.lastUpdate = None
        self.seats = None
        self.updateInterval = None
        self.verifyStatus = None
        self.LicenseProfile = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret

        if name == 'license':
            for key, value in attrs.items():
                setattr(self, key, value)
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'LicenseProfile':
            self.LicenseProfile = value
        else:
            setattr(self, name, value)

    def buildElements(self):
        license = ElementTree.Element('license')

        # build attributes
        for e in self.ValidAttributes:
            if getattr(self, e):
                license.attrib[e] = getattr(self, e)

        if self.LicenseProfile:
            ElementTree.SubElement(
                license, "LicenseProfile").text = self.LicenseProfile

        return license

