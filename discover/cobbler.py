# -*- coding: utf-8 -*-
"""Cobbler module
   Implements the export functionality to Cobbler
"""
from __future__ import print_function, with_statement
import logging
import xmlrpclib
from . import config

logger = logging.getLogger(__name__)

URL = config.settings['cobbler']['url']
LOGIN = config.settings['cobbler']['login']
PASSWORD = config.settings['cobbler']['password']


def add(node):
    """Add a node to cobbler"""
    server = xmlrpclib.Server(URL)
    token = server.login(LOGIN, PASSWORD)
    logger.info('Adding {} to cobbler server {}'.format(node, URL))

    system_id = server.new_system(token)
    server.modify_system(system_id, 'name', node.name, token)
    server.modify_system(system_id, 'hostname', node.name + '.local', token)
    #FIXME: Find a way of assiging the node IP address and selecting the interface
    server.modify_system(system_id, 'modify_interface', {
        #"macaddress-eno1"   : node.switchports['SW14-1']['mac'],
        #"ipaddress-eno1"    : node.bmcaddr.replace('.131.', '.119.'),
        #"netmask-eno1"      : "255.255.0.0",
        #"gateway-eno1"      : "10.119.0.1",
        "macaddress-ens3f0"   : node.get_mac('x1'),
        "ipaddress-ens3f0"    : node.bmcaddr.replace('.131.', '.119.'),
        "netmask-ens3f0"      : "255.255.0.0",
        "gateway-ens3f0"      : "10.119.0.1",
    }, token)
    server.modify_system(system_id, 'gateway', '10.119.0.1', token)
    server.modify_system(system_id, 'profile', 'CentOS7-x86_64', token)
    server.modify_system(system_id, 'power_type', 'imm', token)
    server.modify_system(system_id, 'power_address', node.bmcaddr, token)
    server.modify_system(system_id, 'power_user', 'USERID', token)
    server.modify_system(system_id, 'power_pass', 'PASSW0RD', token)
    server.modify_system(system_id, 'netboot_enabled', True, token)

    server.save_system(system_id, token)
    server.sync(token)
