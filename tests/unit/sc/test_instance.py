#!/usr/bin/env python
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

"Test basic instance and vm"
import unittest
import random
import string
import uuid


from sclib.sc.device import Device, Volume
from sclib.sc.instance import VirtualMachine
from sclib.sc.user import User
from tests.unit.sc import SCBaseTestCase

class SCVirtualMachineTest(SCBaseTestCase):
    def setUp(self):
        SCBaseTestCase.setUp(self)

        #===== implement initial code here for each test =====
        pass

    def testUpdateVM(self):
        self.vms = self.connection.listAllVM()

        for vm in self.vms:
            newvm = self.connection.getVM(vm.imageGUID)
            target = VirtualMachine(self.connection)
            target.imageGUID = newvm.imageGUID
            target.href = newvm.href
            target.imageDescription = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(360))
            target.SecurityGroupGUID = newvm.SecurityGroupGUID
            target.autoProvision = newvm.autoProvision
            updated = target.update()
            self.assertEqual(updated.imageGUID, target.imageGUID)

    def testVMAllDevices(self):

        # list all Computers
        self.vms = self.connection.listAllVM()
        self.assertNotEqual(self.vms, None)

        for vm in self.vms:
            newvm = self.connection.getVM(vm.imageGUID)
            
            for dev in newvm.devices:
                d = newvm.getDevice(dev.id)

    # Some variable
    name = 'template'
    filesystem = 'ext3'
    mountpoint = '/mnt/template'
    RAID_Device1 = '596364df-05f3-48d7-aa86-5223897421d1'
    RAID_Device2 = '31932062-5d64-46a6-b637-ac96dfc0c9e3'

    def testCreateRAID(self):
        vm  = self.connection.getVM('8dbf182f-0a1a-43b5-93ae-b4354252059c')
        devicelist = []
        devicelist.append(self.RAID_Device1)
        devicelist.append(self.RAID_Device2)

        deviceID = str(uuid.uuid4())
        raid = vm.createRAID(self.name, self.filesystem, self.mountpoint, devicelist, deviceID=deviceID)
        self.assertNotEqual(raid, None)

        ret = vm.deleteDevice(deviceID)
        self.assertEqual(ret, 204)

    def testCreateDeleteVM(self):
        vm  = self.connection.getVM('8dbf182f-0a1a-43b5-93ae-b4354252059c')
        res = vm.encrypt()
        self.assertEqual(res, 200)

        #res = vm.cancelPending()
        #self.assertEqual(res, 200)


    def testEncryptAndPending(self):
        pass

    # ===== Test Cases covers Team Tracker =====
    TestVM_ID = "b2f57910-0543-491e-92d7-ab00a47448de"

    def testCase2903(self):
        newvm = self.connection.getVM(self.TestVM_ID)
        target = VirtualMachine(self.connection)
        target.imageGUID = newvm.imageGUID

        # should be removed
        target.SecurityGroupGUID = newvm.SecurityGroupGUID
        target.autoProvision = newvm.autoProvision

        target.imageName = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
        updated = target.update()
        self.assertEqual(updated.imageName, target.imageName)

    def testCase2904(self):
        newvm = self.connection.getVM(self.TestVM_ID)
        target = VirtualMachine(self.connection)
        target.imageGUID = newvm.imageGUID

        # should be removed
        target.SecurityGroupGUID = newvm.SecurityGroupGUID
        target.autoProvision = newvm.autoProvision

        target.imageDescription = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(500))
        updated = target.update()
        self.assertEqual(updated, None)

    def testCase2918(self):
        vm  = self.connection.getVM('8dbf182f-0a1a-43b5-93ae-b4354252059c')
        devicelist = []
        devicelist.append(self.RAID_Device1)
        devicelist.append(self.RAID_Device2)
        deviceID = str(uuid.uuid4())

        # create raid device object
        dev = Device(self.connection)
        dev.name = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(1025))
        dev.msUID = deviceID
        dev.raidLevel = 'RAID0'
        dev.fileSystem = self.filesystem
        dev.volume = Volume(self.connection)
        dev.volume.mountPoint = self.mountpoint

        for d in devicelist:
            new = Device(self.connection)
            new.msUID = d
            dev.subDevices.append(new)

        # call create RAID API
        ret = self.connection.get_status( 'vm/%s/device/raid/' % (vm.imageGUID), 
                                          Device, data=dev.tostring(), method='POST')
        self.assertEqual(ret, 204)

        ret = vm.deleteDevice(deviceID)
        self.assertEqual(ret, 204)

    def testCase2919(self):
        vm  = self.connection.getVM('8dbf182f-0a1a-43b5-93ae-b4354252059c')
        devicelist = []
        devicelist.append(self.RAID_Device1)
        devicelist.append(self.RAID_Device2)
        deviceID = str(uuid.uuid4())

        # create raid device object
        dev = Device(self.connection)
        dev.name = 'testCase2919'
        dev.description = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(1025))
        dev.msUID = deviceID
        dev.raidLevel = 'RAID0'
        dev.fileSystem = self.filesystem
        dev.volume = Volume(self.connection)
        dev.volume.mountPoint = self.mountpoint

        for d in devicelist:
            new = Device(self.connection)
            new.msUID = d
            dev.subDevices.append(new)

        # call create RAID API
        ret = self.connection.get_status( 'vm/%s/device/raid/' % (vm.imageGUID), 
                                          Device, data=dev.tostring(), method='POST')
        self.assertEqual(ret, None)

    def testCase2921(self):
        vm  = self.connection.getVM('8dbf182f-0a1a-43b5-93ae-b4354252059c')
        devicelist = []
        devicelist.append(self.RAID_Device1)
        devicelist.append(self.RAID_Device2)
        deviceID = str(uuid.uuid4())

        # create raid device object
        dev = Device(self.connection)
        dev.name = 'testCase2921'
        dev.msUID = deviceID
        dev.raidLevel = 'RAID0'
        dev.fileSystem = self.filesystem
        dev.volume = Volume(self.connection)
        dev.volume.mountPoint = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(256))

        for d in devicelist:
            new = Device(self.connection)
            new.msUID = d
            dev.subDevices.append(new)

        # call create RAID API
        ret = self.connection.get_status( 'vm/%s/device/raid/' % (vm.imageGUID), 
                                          Device, data=dev.tostring(), method='POST')
        self.assertEqual(ret, None)

    def testCase2922(self):
        vm  = self.connection.getVM('8dbf182f-0a1a-43b5-93ae-b4354252059c')
        devicelist = []
        devicelist.append(self.RAID_Device1)
        devicelist.append(self.RAID_Device2)
        deviceID = str(uuid.uuid4())

        # create raid device object
        dev = Device(self.connection)
        dev.name = 'testCase2921'
        dev.msUID = deviceID
        dev.raidLevel = 'RAID0'
        dev.fileSystem = self.filesystem
        dev.volume = Volume(self.connection)
        dev.volume.mountPoint = ''.join(random.choice('~!@#$%^&*()_+=-][}{;?><,./)') for x in range(256))

        for d in devicelist:
            new = Device(self.connection)
            new.msUID = d
            dev.subDevices.append(new)

        # call create RAID API
        ret = self.connection.get_status( 'vm/%s/device/raid/' % (vm.imageGUID), 
                                          Device, data=dev.tostring(), method='POST')
        self.assertEqual(ret, None)

    def testCase2928(self):
        vm  = self.connection.getVM('8dbf182f-0a1a-43b5-93ae-b4354252059c')
        devicelist = []
        devicelist.append(self.RAID_Device1)
        devicelist.append(self.RAID_Device2)
        deviceID = str(uuid.uuid4())

        # create raid device object
        dev = Device(self.connection)
        dev.name = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(3000))
        dev.msUID = deviceID
        dev.raidLevel = 'RAID0'
        dev.fileSystem = self.filesystem
        dev.volume = Volume(self.connection)
        dev.volume.mountPoint = self.mountpoint

        for d in devicelist:
            new = Device(self.connection)
            new.msUID = d
            dev.subDevices.append(new)

        # call create RAID API
        ret = self.connection.get_status( 'vm/%s/device/raid/' % (vm.imageGUID), 
                                          Device, data=dev.tostring(), method='POST')
        self.assertEqual(ret, None)


if __name__ == '__main__':
    unittest.main()