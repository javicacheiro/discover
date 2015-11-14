# -*- coding: utf-8 -*-
"""Switch module
   Implements the switch object and its functionality
"""
from __future__ import print_function, with_statement
import re
from collections import defaultdict
from snimpy.manager import Manager as M
from snimpy.manager import load


class SNMPClient(object):
    """SNMP operations"""
    def __init__(self, address, community):
        self.address = address
        self.community = community

    def get_mac_table(self):
        """Obtain the MAC table"""
        table = defaultdict(list)
        load('Q-BRIDGE-MIB')
        with M(host=self.address, community=self.community, version=2) as m:
            dbPort = m.dot1qTpFdbPort
            for idx in dbPort:
                vlan, mac = idx
                port = int(dbPort[idx])
                print('{} {} {}'.format(port, mac, vlan))
                table[port].append({"vlan": int(vlan), "mac": mac})
        return table

    def get_port_info_table(self):
        """Obtain the Port table"""
        table = {}
        load('IF-MIB')
        with M(host=self.address, community=self.community, version=2) as m:
            for idx in m.ifName:
                name = m.ifName[idx]
                descr = m.ifDescr[idx]
                # snimpy fails when retrieving an empty value
                try:
                    label = m.ifAlias[idx]
                except UnboundLocalError:
                    label = ''
                print('Adding {} {} {} {}'.format(idx, name, descr, label))
                table[int(idx)] = {"name": name, "descr": descr, "label": label}
        return table


class Switch(object):
    """Representation of a switch"""
    def __init__(self, name, address, community):
        self.name = name
        self.address = address
        self.community = community
        self._snmp = SNMPClient(address, community)
        self.macs = {}
        self.ports = {}

    def update_macs(self):
        """Update the cached mac table"""
        self.macs = self._snmp.get_mac_table()

    def update_port_info(self):
        """Update the cached mac table"""
        self.ports = self._snmp.get_port_info_table()
