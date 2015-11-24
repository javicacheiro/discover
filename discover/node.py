# -*- coding: utf-8 -*-
"""Server Node module
   Implements the node object and its functionality
"""
from __future__ import print_function, with_statement
import subprocess
import re


class BMC(object):
    """BMC representation"""
    def __init__(self, address, user, password):
        self.bmcaddress = address
        self.bmcuser = user
        self.bmcpasswd = password

    def is_on(self):
        """Check the node power status is on"""
        output = self._run_ipmi_cmd('chassis power status')
        if re.search(r'power is on', output, flags=re.IGNORECASE):
            return True
        else:
            return False

    def is_off(self):
        """Check the node power status is off"""
        output = self._run_ipmi_cmd('chassis power status')
        if re.search(r'power is off', output, flags=re.IGNORECASE):
            return True
        else:
            return False

    def power_on(self):
        """Power on the node"""
        return self._run_ipmi_cmd('chassis power on')

    def power_off(self):
        """Power off the node"""
        return self._run_ipmi_cmd('chassis power off')

    def _run_ipmi_cmd(self, cmd):
        """Run a given ipmi command"""
        ipmicmd = 'ipmitool -I lanplus -H {} -U {} -P {} {}'.format(
            self.bmcaddress, self.bmcuser, self.bmcpasswd, cmd)
        try:
            output = subprocess.check_output(ipmicmd, shell=True)
        except subprocess.CalledProcessError as error:
            print('ERROR: IPMI command failed')
            print('  CMD: {}'.format(ipmicmd))
            print('  OUTPUT: {}'.format(error.output))
            print('  Exit status: {}'.format(error.returncode))
        return output


class Node(BMC):
    """Representation of a given node"""
    def __init__(self, name, switchports, bmcaddr, bmcuser, bmcpasswd):
        super(Node, self).__init__(bmcaddr, bmcuser, bmcpasswd)
        self.name = name
        self.switchports = switchports
        self.bmcaddr = bmcaddr
        self.bmcuser = bmcuser
        self.bmcpasswd = bmcpasswd
        self.macs = {}

    def add_mac(self, switch, mac):
        """Associate the given mac to the switchport"""
        self.switchports[switch]['mac'] = mac

    def has_all_macs(self):
        """Confirm if all the MACs are available"""
        for sw, swopts in self.switchports.items():
            if 'mac' not in swopts:
                return False
        return True

    def has_missing_macs(self):
        """Confirm if there are missing MACs"""
        return not self.has_all_macs()
