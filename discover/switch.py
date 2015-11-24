# -*- coding: utf-8 -*-
"""Switch module
   Implements the switch object and its functionality
"""
from __future__ import print_function, with_statement
import logging
from collections import defaultdict
import time
from snimpy.manager import Manager as M
from snimpy.manager import load
from snimpy.snmp import SNMPException
import config

# Number of seconds during which to cache entries
CACHE_TIME = 60
switches = {}

logger = logging.getLogger(__name__)


class SNMPClient(object):
    """SNMP operations"""
    def __init__(self, address, community):
        self.address = address
        self.community = community

    def get_mac_table(self):
        """Obtain the MAC table"""
        table = defaultdict(list)
        load('Q-BRIDGE-MIB')
        logger.info('Retrieving MAC table for {}'.format(self.address))
        with M(host=self.address, community=self.community, version=2) as m:
            dbPort = m.dot1qTpFdbPort
            for idx in dbPort:
                vlan, mac = idx
                # snimpy fails when retrieving an empty value
                try:
                    port = int(dbPort[idx])
                    logger.debug('{} {} {}'.format(port, mac, vlan))
                    table[port].append({"vlan": int(vlan), "mac": mac})
                except SNMPException:
                    logger.error('Unable to get port for mac: {} {}'.format(vlan, mac))
        logger.info('Finished retrieving MAC table for {}'.format(self.address))
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
        self._last_updated_macs = -1

    def update_macs(self):
        """Update the cached mac table"""
        self.macs = self._snmp.get_mac_table()
        self._last_updated_macs = time.time()

    def update_port_info(self):
        """Update the cached port info table"""
        self.ports = self._snmp.get_port_info_table()

    def get_macs_seen_on_port(self, port, vlan):
        """Return the macs seen on a given port an vlan"""
        elapsed_seconds = time.time() - self._last_updated_macs
        if elapsed_seconds > CACHE_TIME:
            logger.info('Cached MAC info expired: querying the switch')
            self.update_macs()
        macs_seen = []
        for entry in self.macs[port]:
            if entry['vlan'] == vlan:
                macs_seen.append(entry['mac'])
        return macs_seen


def query(name, port, vlan=1):
    """Query the MACs seen a given port and vlan of a switch"""
    return switches[name].get_macs_seen_on_port(port, vlan)

# Export all the available switches inside the switches dict
for swname, swcfg in config.switches.items():
    switches[swname] = Switch(swname, swcfg['address'], swcfg['community'])
