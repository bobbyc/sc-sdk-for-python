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

import base64

from sclib.sc.scobject import SCObject
from xml.etree import ElementTree


class User(SCObject):

    ValidAttributes = ['id', 'loginname', 'logintext', 'usertype',
                       'email', 'href', 'isPending', 'isCurrent',
                       'authType', 'ssoIdPName', 'isLicenseUser', 'MFAStatus']

    def __init__(self, connection):
        SCObject.__init__(self, connection)
        # user information
        self.id = None
        self.loginname = None
        self.logintext = None
        self.lastlogintext = None
        self.usertype = None
        self.email = None
        self.href = None
        self.isPending = None
        self.isCurrent = None
        self.authType = None
        self.ssoIdPName = None
        self.isLicensedUser = None
        self.MFAStatus = None
        # contact information
        self.firstName = None
        self.lastName = None
        self.email = None
        # account information
        self.account = None
        self.role = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret

        if name == 'user':
            for key, value in attrs.items():
                setattr(self, key, value)
            return self
        elif name == 'account':
            self.account = Account(connection)
            self.account.startElement(name, attrs, connection)
            return self.account
        elif name == 'role':
            self.role = UserRole(connection)
            self.role.startElement(name, attrs, connection)
            return self.role
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'firstName':
            self.firstName = value
        elif name == 'lastName':
            self.lastName = value
        elif name == 'email':
            self.email = value
        else:
            setattr(self, name, value)

    def buildElements(self):
        user = ElementTree.Element('user')
        user.attrib['version'] = '3.5'

        # build attributes
        if self.id:
            user.attrib['id'] = self.id
        if self.loginname:
            user.attrib['loginname'] = self.loginname
        if self.logintext:
            user.attrib['logintext'] = self.logintext
        if self.lastlogintext:
            user.attrib['lastlogintext'] = self.lastlogintext
        if self.usertype:
            user.attrib['usertype'] = self.usertype
        if self.email:
            user.attrib['email'] = self.email
        if self.href:
            user.attrib['href'] = self.href
        if self.isPending:
            user.attrib['isPending'] = self.isPending
        if self.isCurrent:
            user.attrib['isCurrent'] = self.isCurrent
        if self.authType:
            user.attrib['authType'] = self.authType
        if self.ssoIdPName:
            user.attrib['ssoIdPName'] = self.ssoIdPName
        if self.isLicensedUser:
            user.attrib['isLicensedUser'] = self.isLicensedUser
        if self.MFAStatus:
            user.attrib['MFAStatus'] = self.MFAStatus

        # contact info
        contact = ElementTree.SubElement(user, 'contact')
        if self.firstName:
            ElementTree.SubElement(contact, 'firstName').text = self.firstName
        if self.lastName:
            ElementTree.SubElement(contact, 'lastName').text = self.lastName
        if self.email:
            ElementTree.SubElement(contact, 'email').text = self.email

        # objects
        if self.account:
            user.append(self.account.buildElements())
        if self.role:
            user.append(self.role.buildElements())
        return user

    def setRole(self, role, MFA):
        self.role = UserRole(self.connection)
        self.role.name = role
        self.role.MFAStatus = MFA

    # ----- functions -----

    def delete(self):
        if self.id is None:
            return None

        action = 'user/%s/' % self.id
        response = self.connection.get_status(action, method='DELETE')
        return response == 204

    def update(self):
        # TODO - check more fields
        if self.id is None:
            return None

        action = 'user/%s/' % self.id
        data = ElementTree.tostring(self.buildElements())
        response = self.connection.get_object(
            action, User, data=data, method='POST')
        return response


class Account(SCObject):

    ValidAttributes = ['name', 'id', 'dateFormat',
                       'passphrase', 'sessionTimeout', 'timezoneID']

    def __init__(self, connection):
        SCObject.__init__(self, connection)
        self.name = None
        self.id = None
        self.dateFormat = None
        self.passphrase = None
        self.sessionTimeout = None
        self.timezoneID = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret

        if name == 'account':
            for key, value in attrs.items():
                setattr(self, key, value)
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)

    def buildElements(self):
        account = ElementTree.Element('account')
        if self.id:
            account.attrib['id'] = self.id
        if self.name:
            account.attrib['name'] = self.name
        if self.dateFormat:
            account.attrib['dateFormat'] = self.dateFormat
        if self.passphrase:
            account.attrib['passphrase'] = self.passphrase
        if self.sessionTimeout:
            account.attrib['sessionTimeout'] = self.sessionTimeout
        if self.timezoneID:
            account.attrib['timezoneID'] = self.timezoneID
        return account

    def _update(self, updated):
        self.__dict__.update(updated.__dict__)

    # ----- functions start
    def update(self):
        action = '%s/settings/' % self.connection.REST_ACCOUNT
        data = self.tostring()
        updated = self.connection.get_object(
            action, Account, data=data, method='POST')
        if updated:
            self._update(updated)
            return self

        return updated

    def setPassphrase(self, new):
        action = '%s/passphrase/' % self.connection.REST_ACCOUNT
        self.passphrase = new
        data = self.tostring()
        updated = self.connection.get_object(
            action, Account, data=data, method='POST')
        if updated:
            self._update(updated)
            return self

        return updated


class UserRole(SCObject):

    def __init__(self, connection):
        SCObject.__init__(self, connection)
        self.MFAStatus = None
        self.name = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret

        if name == 'role':
            self.name = attrs['name']
            self.MFAStatus = attrs['MFAStatus']
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)

    def buildElements(self):
        role = ElementTree.Element('role')
        if self.MFAStatus:
            role.attrib['MFAStatus'] = self.MFAStatus
        if self.name:
            role.attrib['name'] = self.name
        return role


class UserRight(SCObject):

    def __init__(self, connection):
        SCObject.__init__(self, connection)
        self.right = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret

        if name == 'right':
            pass
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'right':
            setattr(self, 'right', value)
        else:
            setattr(self, name, value)

    def buildElements(self):
        right = ElementTree.Element('right')
        if self.right:
            role.text['right'] = self.right
        return right
