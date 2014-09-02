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
import xml.sax
import base64

from sclib.exception import SCClientError, SCResponseError
from sclib.connection import SCQueryConnection
from sclib.sc.device import Device
from sclib.sc.user import User, UserRight, UserRole, Account
from sclib.sc.scobject import SCObject
from sclib.sc.instance import VirtualMachine, Instance
from sclib.sc.provider import Provider
from sclib.sc.keyrequest import KeyRequest, RunningVM, RunningDevice
from sclib.sc.securitygroup import SecurityGroup, SecurityRule, SecurityRuleType, SecurityGroupAction, SecurityGroupSetting
from sclib.sc.administration import DSMConnSettings, KMIPConnSettings, Timezone, Language, License

from xml.dom.minidom import parse, parseString
from xml.etree import ElementTree

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto import Hash


class Certificate(SCObject):

    def __init__(self, connection):
        SCObject.__init__(self, connection)
        self.level = None
        self.encoding = None
        self.certificate = None
        self.publickey = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret

        if name == 'certificate':
            self.id = attrs['level']
            self.encoding = attrs['encoding']
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'certificate':
            self.certificate = value
            self.publickey = """-----BEGIN RSA PUBLIC KEY-----\n%s\n-----END RSA PUBLIC KEY-----\n""" % (
                self.certificate)
        else:
            setattr(self, name, value)

    def encryptData(self, data):
        if self.certificate:
            publickey = RSA.importKey(self.publickey).publickey()
            cipher = PKCS1_OAEP.new(publickey, Hash.SHA256)
            encrypted = cipher.encrypt(bytes(data))
            return base64.b64encode(encrypted)
        return None


class Authentication(SCObject):

    # Valid xml object attributes
    ValidAttributes = ['id', 'token', 'expires', 'data', 'accountId']

    def __init__(self, connection, tag='authentication'):
        SCObject.__init__(self, connection, tag)
        self.id = None
        self.token = None
        self.expires = None
        self.data = None
        self.accountId = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret

        if name == 'authenticationResult':
            self.id = attrs['id']
            self.token = attrs['token']
            self.expires = attrs['expires']
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)

    def buildElements(self, elements=None):
        authentication = ElementTree.Element('authentication')

        # build attributes
        for attr in self.ValidAttributes:
            if getattr(self, attr):
                authentication.attrib[attr] = getattr(self, attr)

        return authentication

    def isAuthenticated(self):
        return self.token is not None


class SCConnection(SCQueryConnection):

    REST_PUBLIC_CERTIFICATE = 'PublicCertificate'
    REST_BASIC_AUTH = 'userBasicAuth'
    REST_DEVICE = 'device'
    REST_SECURITY_GROUP = 'SecurityGroup'
    REST_SECURITY_GROUP_SETTING = 'securityGroupSetting'
    REST_SECURITY_RULE = 'SecurityRule'
    REST_SECURITY_RULE_TYPE = 'SecurityRule'
    REST_USER = 'user'
    REST_USER_RIGHT = 'rights'
    REST_USER_ROLE = 'roles'
    REST_VM = 'vm'
    REST_PROVIDER = 'provider'
    REST_RUNNING_VM = 'runningVM'
    REST_KEY_REQUEST = 'keyRequest'
    REST_DSM_SETTING = 'dsmConnSettings'
    REST_KMIP_SETTING = 'kmip'
    REST_ACCOUNT = 'acctData'
    REST_ACCOUNTS = 'accounts'
    REST_TIMEZONE = 'timezone'
    REST_STATUS = 'status'
    REST_ENTRYPOINT = 'entrypoint'
    REST_LICENSE = 'licenses'
    REST_LANGUAGE = 'language'

    def __init__(self, host_base, broker_name=None, broker_passphase=None, https=True):
        SCQueryConnection.__init__(
            self, host_base, broker_name, broker_passphase, https)

        # members
        self.__authentication = None
        self.__certificate = None
        self.__user = None
        self.__account = None

    # ---------------
    # properties
    # ---------------
    @property
    def authentication(self):
        return self.__authentication

    @property
    def certificate(self):
        return self.__certificate

    @property
    def user(self):
        return self.__user

    @property
    def account(self):
        return self.__account

    # ---------------
    # member functions
    # ---------------
    def getCertificate(self):
        self.__certificate = self.get_object('%s/' % (self.REST_PUBLIC_CERTIFICATE),
                                             Certificate)
        if not self.__certificate:
            raise SCResponseError('4xx', "Unknown error")

        return self.__certificate

    def basicAuth(self, name, password):

        if self.certificate is None:
            self.getCertificate()

        # build authentication request
        auth_name = base64.b64encode(name)
        auth_req = Authentication(self)
        auth_req.data = self.certificate.encryptData(password)
        req_data = ElementTree.tostring(auth_req.buildElements())

        auth = self.get_object('%s/%s' % (self.REST_BASIC_AUTH, auth_name),
                               Authentication, data=req_data, method='POST')
        if auth:
            self.__authentication = auth
            self.headers['X-UserSession'] = self.authentication.token
            self.user = self.getUser(auth.id)
            self.account = self.getAccount()
        return self.authentication

    def isAuthenticated(self):
        if self.authentication is None:
            raise SCClientError(
                'Connection abort. Needs Authentication first!')

        return True

    #=========================================================================
    # function - Policy/SecurityGroup
    #=========================================================================
    def listAllSecurityGroup(self):
        if self.authentication is None:
            return None

        return self.get_list('%s/' % (self.REST_SECURITY_GROUP),
                             [('securityGroup', SecurityGroup)])

    def getSecurityGroup(self, id):
        if self.authentication is None:
            return None

        rule = self.get_object('%s/%s/' % (self.REST_SECURITY_GROUP, id),
                               SecurityGroup)
        return rule

    def createSecurityGroup(self, objSecurityGroup):
        if self.authentication is None:
            return None

        #policy = SecurityGroup(self)
        #policy.name = name
        # Test default value here
        #========================
        if isinstance(objSecurityGroup, SecurityGroup):
            data = objSecurityGroup.tostring()
        else:
            data = ''
            
        policy = self.get_object('%s/' % (self.REST_SECURITY_GROUP),
                                 SecurityGroup, data=data, method='POST')
        return policy

    def deleteSecurityGroup(self, id):
        if self.authentication is None:
            return None

        status = self.get_status('%s/%s/' % (self.REST_SECURITY_GROUP, id),
                                 method='DELETE')
        return status

    def listAllSecurityRuleTypes(self):
        if self.authentication is None:
            return None

        return self.get_list('%s' % (self.REST_SECURITY_RULE_TYPE),
                             [('securityRuleType', SecurityRuleType)])

    def getSecurityRuleType(self, id):
        if self.authentication is None:
            return None

        rule = self.get_object('%s/%s/' % (self.REST_SECURITY_RULE_TYPE, id),
                               SecurityRuleType)
        return rule

    def getSecurityGroupSetting(self):
        if self.isAuthenticated() is False:
            return None

        return self.get_object(self.REST_SECURITY_GROUP_SETTING, SecurityGroupSetting)

    #=========================================================================
    # function - User
    #=========================================================================
    def listAllUsers(self):
        if self.isAuthenticated() is False:
            return None

        return self.get_list('%s/' % (self.REST_USER),
                             [('user', User)])

    def createUser(self, login, logintext, usertype='localuser',
                   firstname='', lastname='', email='',
                   role='Administrator', MFA='false'):

        if self.isAuthenticated() is False:
            return None

        user = User(self)
        user.loginname = login
        user.logintext = base64.b64encode(logintext)
        user.usertype = usertype
        user.firstName = firstname
        user.lastName = lastname
        user.email = email
        user.name = role
        user.MFAStatus = MFA
        user.setRole(role, MFA)
        data = ElementTree.tostring(user.buildElements())
        return self.get_object('%s/' % (self.REST_USER),
                               User, data=data, method='POST')

    def getUser(self, id):
        if self.isAuthenticated() is False:
            return None

        return self.get_object('%s/%s/' % (self.REST_USER, id),
                               User)

    def changeUserPassword(self, lastlogintext, newlogintext):

        if self.isAuthenticated() is False:
            return None

        params = {}
        user = User(self)
        user.lastlogintext = base64.b64encode(lastlogintext)
        user.logintext = base64.b64encode(newlogintext)
        data = ElementTree.tostring(user.buildElements())
        return self.get_status('user/%s/%s/' % ('logintext', self.authentication.id),
                               data=data, method='POST')

    def getUserRights(self):
        if self.isAuthenticated() is False:
            return None

        return self.get_list('%s/' % (self.REST_USER_RIGHT),
                             [('userRights', UserRight)])

    #=========================================================================
    # virtual machine function
    #=========================================================================
    def listAllVM(self):
        if self.isAuthenticated() is False:
            return None

        return self.get_list('%s' % (self.REST_VM),
                             [('vm', VirtualMachine)])

    def getVM(self, id):
        if self.isAuthenticated() is False:
            return None

        return self.get_object('%s/%s/' % (self.REST_VM, id),
                               VirtualMachine)

    #=========================================================================
    # Provider function
    #=========================================================================
    def listAllProvider(self):
        if self.isAuthenticated() is False:
            return None

        return self.get_list('%s' % (self.REST_PROVIDER),
                             [('provider', Provider)])

    def getProvider(self, name):
        if self.isAuthenticated() is False:
            return None

        return self.get_object('%s/%s/' % (self.REST_PROVIDER, name),
                               Provider)

    #-------------------------------------------------------------------------
    # key request
    #-------------------------------------------------------------------------
    def listAllRunningVM(self):
        if self.isAuthenticated() is False:
            return None

        return self.get_list('%s' % (self.REST_RUNNING_VM),
                             [('runningVM', RunningVM)])

    def listKeyRequest(self, id):
        if self.isAuthenticated() is False:
            return None

        return self.get_object('%s/%s/%s/' % (self.REST_RUNNING_VM, self.REST_KEY_REQUEST, id),
                               KeyRequest)

    #-------------------------------------------------------------------------
    # Administration - Settings
    #-------------------------------------------------------------------------
    def getDSMSetting(self):
        if self.isAuthenticated() is False:
            return None

        return self.get_object('%s/' % (self.REST_DSM_SETTING),
                               DSMConnSettings)

    def getKMIPSetting(self):
        if self.isAuthenticated() is False:
            return None

        return self.get_object('%s/%s/' % (self.REST_KMIP_SETTING, 'setting'),
                               KMIPConnSettings)

    #-------------------------------------------------------------------------
    # Administration - Account
    #-------------------------------------------------------------------------
    def getAccount(self):
        if self.isAuthenticated() is False:
            return None

        # get account info with current connection
        return self.get_object('%s/' % (self.REST_ACCOUNT), Account)

    #-------------------------------------------------------------------------
    # Administration - Timezon
    #-------------------------------------------------------------------------
    def listTimezone(self):
        if self.isAuthenticated() is False:
            return None

        # get account info with current connection
        return self.get_list('%s/' % (self.REST_TIMEZONE),
                             [('timezoneList', Timezone)])

    #-------------------------------------------------------------------------
    # Administration - Server Status
    #-------------------------------------------------------------------------
    def getEntrypoint(self):
        if self.isAuthenticated() is False:
            return None

        # get account info with current connection
        return self.get_status('%s/' % (self.REST_ENTRYPOINT))

    #-------------------------------------------------------------------------
    # Administration - License status
    #-------------------------------------------------------------------------
    def getLicense(self):
        if self.isAuthenticated() is False:
            return None

        # get account info with current connection
        return self.get_object('%s/' % (self.REST_LICENSE), License)

    def setLicense(self, ac):
        if self.isAuthenticated() is False:
            return None

        objLicense = License(self)
        objLicense.ac = ac
        
        action = '%s/' % (self.REST_LICENSE)
        data = objLicense.tostring()
        
        return self.get_status(action, data=data, method='POST')

    #-------------------------------------------------------------------------
    # Administration - Language
    #-------------------------------------------------------------------------
    def listLanguages(self):
        if self.isAuthenticated() is False:
            return None

        # get account info with current connection
        return self.get_list('%s/' % (self.REST_LANGUAGE),
                             [('language', Language)])
