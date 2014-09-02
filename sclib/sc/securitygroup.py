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
from sclib.sc.device import Device
from sclib.sc.instance import VirtualMachine
from xml.etree import ElementTree


class SecurityGroupAction(SCObject):

    ValidAttributes = ['action', 'autoDelay', 'enable']

    # member functions
    def __init__(self, connection):
        SCObject.__init__(self, connection)
        self.action = None
        self.autoDelay = None
        self.enable = None


class SecurityGroup(SCObject):

    ValidAttributes = ['id', 'name', 'href',
                       'isDeleteble', 'isNameEditable',
                       'lastModified', 'ruleCount', 'imageCount',
                       'EnableIC', 'ICAction', 'PostponeEnable',
                       'RevokeIntervalType', 'RevokeIntervalNumber']

    # member functions
    def __init__(self, connection):
        SCObject.__init__(self, connection)

        # member initialization
        self.id = None
        self.name = None
        self.isDeleteble = None
        self.isNameEditable = None
        self.href = None
        self.lastModified = None
        self.ruleCount = None
        self.EnableIC = None
        self.ICAction = None
        self.PostponeEnable = None
        self.RevokeIntervalType = None
        self.RevokeIntervalNumber = None
        self.description = None
        self.imageCount = None
        # rules
        self.securityRuleList = ResultSet(
            [('securityRule', SecurityRule)], 'securityRuleList')
        # action
        self.successAction = None
        self.failedAction = None
        self.integrityAction = None
        # vm
        self.__vmList = ResultSet([('vm', VirtualMachine)], 'vmList')

    # Property function (vmList)
    @property
    def vmList(self):
        return self.__vmList

    def addVM(self, vm):
        ret = False
        if isinstance(vm, VirtualMachine):
            self.__vmList.append(vm)
            self.imageCount = str(len(self.__vmList))
            ret = True
        return ret

    # Parse functions

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret

        if name == 'securityGroup':
            for key, value in attrs.items():
                if key in self.ValidAttributes:
                    setattr(self, key, value)
            return self
        elif name == 'securityRuleList':
            if not self.securityRuleList:
                self.securityRuleList = ResultSet(
                    [('securityRule', SecurityRule)], name)
            return self.securityRuleList
        elif name == 'vmList':
            self.__vmList = ResultSet([('vm', VirtualMachine)], name)
            return self.vmList
        elif name == 'successAction':
            self.successAction = SecurityGroupAction(connection, name)
            return self.successAction.startElement(name, attrs, connection)
        elif name == 'failedAction':
            self.failedAction = SecurityGroupAction(connection, name)
            return self.failedAction.startElement(name, attrs, connection)
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'description':
            self.description = value
        else:
            setattr(self, name, value)

    def buildElements(self):
        group = ElementTree.Element('securityGroup')

        #===================================================================
        # build Required elements
        for e in self.ValidAttributes:
            if getattr(self, e, None):
                group.attrib[e] = getattr(self, e)

        if self.description:
            ElementTree.SubElement(
                group, "description").text = self.description

        # actions
        if self.successAction:
            group.append(self.successAction.buildElements())
        if self.failedAction:
            group.append(self.failedAction.buildElements())

        if self.vmList:
            # ===== Here is workaround to build vmList =====
            vmList = ElementTree.SubElement(group, 'vmList')
            vms = ElementTree.SubElement(vmList, 'vms')
            for vm in self.vmList:
                vms.append(vm.buildElements())

        # append security rule list
        if self.securityRuleList:
            group.append(self.securityRuleList.buildElements())

        return group

    # ---------- function ----------

    def update(self):
        # Build XML elements structures
        action = '%s/%s/' % (self.connection.REST_SECURITY_GROUP, self.id)
        data = self.tostring()
        response = self.connection.get_status(action, data=data, method='POST')
        return response


class SecurityRule(SCObject):

    ValidAttributes = ['id', 'description', 'matchType', 'dataMissing']

    def __init__(self, connection):
        SCObject.__init__(self, connection)

        # member initialization
        self.id = None
        self.description = None
        self.matchType = None
        self.dataMissing = None
        # inner objects
        self.securityRuleType = None
        self.deviceList = None
        self.securityRuleConditionList = ResultSet([('securityRuleCondition', SecurityRuleCondition)], "securityRuleConditionList")

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret

        if name == 'securityRule':
            for key, value in attrs.items():
                setattr(self, key, value)
        elif name == 'securityRuleType':
            self.securityRuleType = SecurityRuleType(connection)
            self.securityRuleType.startElement(name, attrs, connection)
            return self.securityRuleType
        elif name == 'deviceList':
            self.deviceList = ResultSet([('device', Device)], name)
            return self.deviceList
        elif name == 'securityRuleConditionList':
            self.securityRuleConditionList = ResultSet(
                [('securityRuleCondition', SecurityRuleCondition)], name)
            return self.securityRuleConditionList
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)

    def buildElements(self):
        rule = ElementTree.Element('securityRule')

        #===================================================================
        # Required elements
        # build attributes
        for e in self.ValidAttributes:
            if getattr(self, e):
                rule.attrib[e] = getattr(self, e)

        #===================================================================
        # Optional elements

        # append inner objects
        if self.securityRuleType:
            rule.append(self.securityRuleType.buildElements())
        if self.securityRuleConditionList:
            rule.append(self.securityRuleConditionList.buildElements())
        # TODO - Add actions

        return rule

    # ----- operation -----
    def update(self):
        pass


class SecurityRuleCondition(SCObject):
    ValidAttributes = ['evaluator', 'expectedValue']

    def __init__(self, connection):
        SCObject.__init__(self, connection)

        # member initialization
        self.evaluator = None
        self.expectedValue = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret

        if name == 'securityRuleCondition':
            for key, value in attrs.items():
                setattr(self, key, value)
            return self
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)

    def buildElements(self):
        condition = ElementTree.Element('securityRuleCondition')

        # user info
        if self.evaluator:
            condition.attrib['evaluator'] = self.evaluator
        if self.expectedValue:
            condition.attrib['expectedValue'] = self.expectedValue
        # actions
        return condition


class SecurityRuleType(SCObject):
    ValidAttributes = ['id', 'name', 'evaluator',
                       'context', 'dataType', 'description']

    def __init__(self, connection):
        SCObject.__init__(self, connection)

        # member initialization
        self.id = None
        self.name = None
        self.evaluator = None
        self.context = None
        self.dataType = None
        self.description = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return retn

        if name == 'securityRuleType':
            for key, value in attrs.items():
                setattr(self, key, value)
            return self
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'description':
            self.description = value
        else:
            setattr(self, name, value)

    def buildElements(self):
        type = ElementTree.Element('securityRuleType')

        # 'Required' fields
        # user info
        if self.id:
            type.attrib['id'] = self.id
        if self.name:
            type.attrib['name'] = self.name
        if self.evaluator:
            type.attrib['evaluator'] = self.evaluator
        if self.context:
            type.attrib['context'] = self.context
        if self.dataType:
            type.attrib['dataType'] = self.dataType
        if self.description:
            type.attrib['description'] = self.description
        # actions

        return type


class SecurityGroupAction(SCObject):
    ValidAttributes = ['action', 'autoDelay']

    # constant
    ManualApprove = 'ManualApprove'
    Approve = 'Approve'
    Deny = 'Deny'

    def __init__(self, connection, actionName, action=None, autoDelay='-1'):
        SCObject.__init__(self, connection)

        # member initialization
        self.name = actionName
        self.action = action
        self.autoDelay = autoDelay

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret

        if name == self.name:
            for key, value in attrs.items():
                setattr(self, key, value)
            return self
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)

    def buildElements(self):
        action = ElementTree.Element(self.name)

        # user info
        if self.action:
            action.attrib['action'] = self.action
        if self.autoDelay:
            action.attrib['autoDelay'] = self.autoDelay
        # actions
        return action
    

class SecurityGroupSetting(SCObject):

    ValidAttributes = ['ScheduleType', 'ScheduleIntervalTime', 'ScheduleIntervalPeriod', 'ScheduleIntervalDay',
                       'ReAttemptInterval', 'ReAttemptIntervalType', 'ReAttemptICRepeat']

    def __init__(self, connection):
        SCObject.__init__(self, connection)
        self.ScheduleType = None
        self.ScheduleIntervalTime = None
        self.ScheduleIntervalPeriod = None
        self.ScheduleIntervalDay = None
        self.ReAttemptInterval = None
        self.ReAttemptIntervalType = None
        self.ReAttemptICRepeat = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret

        if name == 'securityGroupSetting':
            for key, value in attrs.items():
                if key in self.ValidAttributes:
                    setattr(self, key, value)
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'ScheduleType':
            self.ScheduleType = value
        elif name == 'ScheduleIntervalTime':
            self.ScheduleIntervalTime = value
        elif name == 'ScheduleIntervalPeriod':
            self.ScheduleIntervalPeriod = value
        elif name == 'ScheduleIntervalDay':
            self.ScheduleIntervalDay = value
        elif name == 'ReAttemptInterval':
            self.ReAttemptInterval = value
        elif name == 'ReAttemptIntervalType':
            self.ReAttemptIntervalType = value
        elif name == 'ReAttemptICRepeat':
            self.ReAttemptICRepeat = value

    def buildElements(self):
        setting = ElementTree.Element('securityGroupSetting')

        # Set all valid Elements
        if self.ScheduleType:
            setting.attrib['ScheduleType'] = self.ScheduleType
        if self.ScheduleIntervalTime:
            setting.attrib['ScheduleIntervalTime'] = self.ScheduleIntervalTime
        if self.ScheduleIntervalPeriod:
            setting.attrib['ScheduleIntervalPeriod'] = self.ScheduleIntervalPeriod
        if self.ScheduleIntervalDay:
            setting.attrib['ScheduleIntervalDay'] = self.ScheduleIntervalDay
        if self.ReAttemptInterval:
            setting.attrib['ReAttemptInterval'] = self.ReAttemptInterval
        if self.ReAttemptIntervalType:
            setting.attrib['ReAttemptIntervalType'] = self.ReAttemptIntervalType
        if self.ReAttemptICRepeat:
            setting.attrib['ReAttemptICRepeat'] = self.ReAttemptICRepeat

        return setting

    def update(self):
        #action = 'securityGroupSetting/'
        action = '%s/' % (self.connection.REST_SECURITY_GROUP_SETTING)
        data = self.tostring()
        response = self.connection.get_status(action, data=data, method='POST')
        return response

