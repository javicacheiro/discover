# -*- coding: utf-8 -*-
"""Server Node module
   Implements the node object and its functionality
"""
from __future__ import print_function, with_statement
import subprocess
import re
import time
from .helpers import ToDictMixin

# Seconds to wait for the OS to shutdown gracefully
SHUTDOWN_GRACE_TIME = 5


class MacAddressNotFoundError(Exception):
    """MAC Address not found"""
    pass


class BMC(object):
    """BMC representation"""
    def __init__(self, address, user, password):
        self.address = address
        self.user = user
        self.password = password

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
        # First try soft-shutdown of OS via ACPI
        self._run_ipmi_cmd('chassis power soft')
        for _ in range(SHUTDOWN_GRACE_TIME):
            time.sleep(1)
            if self.is_off():
                return True
        return self._run_ipmi_cmd('chassis power off')

    def activate_pxe(self):
        """Temporarily activate pxe for next boot"""
        return self._run_ipmi_cmd('chassis bootdev pxe')

    def _run_ipmi_cmd(self, cmd):
        """Run a given ipmi command"""
        ipmicmd = 'ipmitool -I lanplus -H {} -U {} -P {} {}'.format(
            self.address, self.user, self.password, cmd)
        try:
            output = subprocess.check_output(ipmicmd, shell=True)
        except subprocess.CalledProcessError as error:
            print('ERROR: IPMI command failed')
            print('  CMD: {}'.format(ipmicmd))
            print('  OUTPUT: {}'.format(error.output))
            print('  Exit status: {}'.format(error.returncode))
        return output


class Node(ToDictMixin):
    """Representation of a given node"""
    def __init__(self, name, switchports={}, bmcaddr='', bmcuser='', bmcpasswd=''):
        self.bmc = BMC(bmcaddr, bmcuser, bmcpasswd)
        self.name = name
        self.switchports = switchports

    def __repr__(self):
        return ('<{}({}, switchports={}, bmcaddr={}, bmcuser={}, bmcpasswd={})>'
                .format(
                    self.__class__, self.name, self.switchports,
                    self.bmcaddr, self.bmcuser, self.bmcpasswd
                ))

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

    def get_mac(self, nic):
        """Get the MAC address for the given NIC interface"""
        for sw, swopts in self.switchports.items():
            if swopts['nic'] == nic:
                return swopts['mac']
        raise MacAddressNotFoundError('No MAC address found for NIC {}'.format(nic))
