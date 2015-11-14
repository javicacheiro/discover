# -*- coding: utf-8 -*-
"""Discovery module
   Implements the discovery of MAC addresses.
"""
from __future__ import print_function, with_statement
import os
from .node import Node
from .switch import Switch

class MACFinder():
    """Discovery object

    Runs the discovery
    """

    def __init__(self, cfg):
        self.cfg = cfg

    def find_node(self, nodename):
        """Find the MAC addresses of a given node"""
        node = self._query_switches(self, nodename)
        if node.has_all_macs():
            pass

    def _query_switches(self, nodename):
        """Query switches for the MACs of the given node"""
        switches = {}
        switchports = self.cfg.nodes[nodename]['switchports']
        # Prepare the required switch objects
        for switchname in switchports:
            s = self.cfg.switches[switchname]
            switches[switchname] = Switch(s.address, s.community)
        for switch in switches.values():
            print('== Updating MACs for switch {}'.format(switch.name))
            switch.update_macs()
            switch.macs[switchports[switch]]

    
