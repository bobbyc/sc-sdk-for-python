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

from sclib.resultset import ResultSet
from sclib.sc.scobject import SCObject
from sclib.sc.instance import VirtualMachine
from sclib.sc.device import Device
from xml.etree import ElementTree


class KeyRequest(SCObject):

    ValidAttributes = ['requestID', 'requested', 'deviceKeyRequestState',
                       'href']

    def __init__(self, connection, tag='runningVMKeyRequest'):
        SCObject.__init__(self, connection, tag)
        self.requestID = None
        self.requested = None
        self.deviceKeyRequestState = None
        self.href = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret

        if name == self.tag:
            for key, value in attrs.items():
                setattr(self, key, value)
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)

    def buildElements(self):
        keyrequest = ElementTree.Element(self.tag)

        # Set all valid attributes
        for attr in self.ValidAttributes:
            if getattr(self, attr):
                keyrequest.attrib[attr] = getattr(self, attr)

        return keyrequest

    # Key request operators
    def approve(self):
        return self.connection.get_status('%s/%s/%s/%s/' % (self.connection.REST_RUNNING_VM,
                                                            self.connection.REST_KEY_REQUEST,
                                                            self.requestID,
                                                            'approve'),
                                          data=self.tostring(),
                                          method='POST')

    def deny(self):
        return self.connection.get_status('%s/%s/%s/%s/' % (self.connection.REST_RUNNING_VM,
                                                            self.connection.REST_KEY_REQUEST,
                                                            self.requestID,
                                                            'deny'),
                                          data=self.tostring(),
                                          method='POST')

    def revoke(self):
        return self.connection.get_status('%s/%s/%s/%s/' % (self.connection.REST_RUNNING_VM,
                                                            self.connection.REST_KEY_REQUEST,
                                                            self.requestID,
                                                            'revoke'),
                                          data=self.tostring(),
                                          method='POST')

    def ignore(self):
        return self.connection.get_status('%s/%s/%s/%s/' % (self.connection.REST_RUNNING_VM,
                                                            self.connection.REST_KEY_REQUEST,
                                                            self.requestID,
                                                            'ignore'),
                                          data=self.tostring(),
                                          method='POST')

    def run_icm(self):
        return self.connection.get_status('%s/%s/%s/%s/' % (self.connection.REST_RUNNING_VM,
                                                            self.connection.REST_KEY_REQUEST,
                                                            self.requestID,
                                                            'runicm'),
                                          data=self.tostring(),
                                          method='POST')


class RunningDevice(Device):

    ValidAttributes = ['deviceRequestID', 'allowKeyAction', 'KeyDeliveryStatus',
                       'integrity', 'deviceKeyRequestState']

    def __init__(self, connection, tag='runningVMDevice'):
        Device.__init__(self, connection, tag)
        self.deviceRequestID = None
        self.allowKeyAction = None
        self.KeyDeliveryStatus = None
        self.integrity = None
        self.deviceKeyRequestState = None
         # Device list
        self.device = None

    def startElement(self, name, attrs, connection):
        ret = Device.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret

        if name == self.tag:
            for key, value in attrs.items():
                setattr(self, key, value)
        elif name == 'device':
            self.device = Device(connection)
            self.device.startElement(name, attrs, connection)
            return self.device
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)

    def buildElements(self):
        runningVMDevice = ElementTree.Element('runningVMDevice')

        # Set all valid attributes
        for attr in self.ValidAttributes:
            if getattr(self, attr):
                runningVMDevice.attrib[attr] = getattr(self, attr)

                # append inner objects
        if getattr(self, 'device'):
            runningVMDevice.append(self.device.buildElements())

        return runningVMDevice


class RunningVM(VirtualMachine):

    ValidAttributes = ['providerName', 'providerLocation']

    def __init__(self, connection, tag='runningVM'):
        VirtualMachine.__init__(self, connection, tag)
        self.providerName = None
        self.providerLocation = None
        # KeyRequest list
        self.runningVMKeyRequest = None
        # running Device list
        self.runningVMDevices = ResultSet(
            [('runningVMDevices', RunningDevice)], 'runningVMDevice')

    def startElement(self, name, attrs, connection):
        ret = VirtualMachine.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret

        if name == self.tag:
            for key, value in attrs.items():
                setattr(self, key, value)
        elif name == 'runningVMKeyRequest':
            self.runningVMKeyRequest = KeyRequest(connection)
            self.runningVMKeyRequest.startElement(name, attrs, connection)
            return self.runningVMKeyRequest
        elif name == 'runningVMDevices':
            self.runningVMDevices = ResultSet(
                [('runningVMDevice', RunningDevice)], name)
            return self.runningVMDevices
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)

    def buildElements(self):
        runningVM = ElementTree.Element('runningVM')

        # Set all valid attributes
        for attr in VirtualMachine.ValidAttributes:
            if getattr(self, attr):
                runningVM.attrib[attr] = getattr(self, attr)

        for attr in self.ValidAttributes:
            if getattr(self, attr):
                runningVM.attrib[attr] = getattr(self, attr)

        # append inner objects
        if getattr(self, 'runningVMKeyRequest'):
            runningVM.append(self.runningVMKeyRequest.buildElements())
        if getattr(self, 'runningVMDevices'):
            runningVM.append(self.runningVMDevices.buildElements())

        return runningVM
