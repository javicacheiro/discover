# -*- coding: utf-8 -*-
"""Inventory module
   Implements the inventory functionality
"""
from __future__ import print_function, with_statement
import os
import glob
import re
import logging
import cPickle as pickle
from . import cobbler

logger = logging.getLogger(__name__)

DEFAULT_DB_DIR = os.path.expanduser('~/.discover/db')

if not os.path.exists(DEFAULT_DB_DIR):
    os.makedirs(DEFAULT_DB_DIR)


class NodeNotFoundError(Exception):
    pass


def save(node):
    """Save a given node in the inventory"""
    filename = os.path.join(DEFAULT_DB_DIR, node.name + '.p')
    with open(filename, 'w') as dumpfile:
        logger.info('Adding {} to the inventory database'.format(node.name))
        pickle.dump(node, dumpfile)


def load(nodename):
    """Load a given node from the inventory"""
    #FIXME: Detect if there are changes in the node configuration so they
    #       are applied to the inventory object if needed
    filename = os.path.join(DEFAULT_DB_DIR, nodename + '.p')
    try:
        with open(filename, 'r') as dumpfile:
            return pickle.load(dumpfile)
    except IOError:
        logger.info('Node {} not found in inventory'.format(nodename))
        raise NodeNotFoundError('Node not found in inventory')


def show(nodename='all'):
    """Show the information about nodes in the inventory"""
    if nodename.lower() == 'all':
        nodes = _load_all_nodes_from_inventory()
        nics = _nic_names(nodes)
        print('{:10}'.format('Nodename') + ''.join('   {:^17}'.format(nic) for nic in nics))
        print('-'*(10 + 20*len(nics)))
        # Sort the nodes in numerical order: pad the numeric parts for the right output
        #nodes.sort(key=lambda node: re.sub('(\d+)', lambda m: '{:08d}'.format(int(m.group(0))), node.name))
        digits = re.compile(r'(\d+)')

        def expanded_nodename(node):
            def pad_numbers(m):
                return '{:08d}'.format(int(m.group(0)))
            return digits.sub(pad_numbers, node.name)

        nodes.sort(key=expanded_nodename)
        for node in nodes:
            _print_node(node, nics)
    else:
        filename = os.path.join(DEFAULT_DB_DIR, nodename + '.p')
        with open(filename) as nodefile:
            node = pickle.load(nodefile)
        nics = set()
        for sw, opts in node.switchports.items():
            nics.add(opts['nic'])
        _print_node(node, nics)


def _load_all_nodes_from_inventory():
    """Loads all the nodes available in the inventory"""
    nodes = []
    for filename in glob.glob(os.path.join(DEFAULT_DB_DIR, '*.p')):
        with open(filename) as nodefile:
            nodes.append(pickle.load(nodefile))
    return nodes


def _nic_names(nodes):
    """Get the names of the NICs of the given nodes"""
    nics = set()
    for node in nodes:
        for sw, opts in node.switchports.items():
            nics.add(opts['nic'])
    return nics


def _print_node(node, nics):
    """Print the information about a given node"""
    macs = {}
    for sw, opts in node.switchports.items():
        if 'mac' in opts:
            macs[opts['nic']] = opts['mac']
        else:
            macs[opts['nic']] = 'UNKNOWN'
    for nic in nics:
        if nic not in macs:
            macs[nic] = 'N/A'
    print('{:10}'.format(node.name) + ''.join('   {:17}'.format(macs[nic]) for nic in nics))


def _export_node_to_csv(node, nics):
    """Export to csv a given node"""
    macs = {}
    for sw, opts in node.switchports.items():
        if 'mac' in opts:
            macs[opts['nic']] = opts['mac']
        else:
            macs[opts['nic']] = 'UNKNOWN'
    # Mark non-existent NICs as not available for this node 
    for nic in nics:
        if nic not in macs:
            macs[nic] = 'N/A'
    print('{},'.format(node.name) + ','.join(macs[nic] for nic in nics))


def export_to_csv(nodename='all'):
    """Show the information about nodes in the inventory"""
    if nodename.lower() == 'all':
        nodes = _load_all_nodes_from_inventory()
        nics = _nic_names(nodes)
        print('#node,' + ','.join(nics))
        for node in nodes:
            _export_node_to_csv(node, nics)
    else:
        filename = os.path.join(DEFAULT_DB_DIR, nodename + '.p')
        with open(filename) as nodefile:
            node = pickle.load(nodefile)
        nics = set()
        for sw, opts in node.switchports.items():
            nics.add(opts['nic'])
        print('#node,' + ','.join(nics))
        _export_node_to_csv(node, nics)


def export_to_cobbler(nodename):
    """Export the inventory to cobbler format"""
    if nodename.lower() == 'all':
        nodes = _load_all_nodes_from_inventory()
        for node in nodes:
            cobbler.add(node)
    else:
        node = load(nodename)
        cobbler.add(node)
