# -*- coding: utf-8 -*-
"""Inventory module
   Implements the inventory functionality
"""
from __future__ import print_function, with_statement
import os
import glob
import logging
import cPickle as pickle

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
    filename = os.path.join(DEFAULT_DB_DIR, nodename + '.p')
    try:
        with open(filename, 'r') as dumpfile:
            return pickle.load(dumpfile)
    except IOError:
        logger.info('Node {} not found in inventory'.format(nodename))
        raise NodeNotFoundError('Node not found in inventory')


def show():
    """Show the information about nodes in the inventory"""
    print('#node x1 n1 n2')
    for filename in glob.glob(os.path.join(DEFAULT_DB_DIR, '*.p')):
        with open(filename) as nodefile:
            node = pickle.load(nodefile)
            print_node(node)


def print_node(node):
    """Print the information about a given node"""
    macs = {}
    for sw, opts in node.switchports.items():
        if 'mac' in opts:
            macs[opts['nic']] = opts['mac']
        else:
            macs[opts['nic']] = 'UNKNOWN'
    #TODO: Make the NIC printing generic: sorted(macs), homogeneous groups of nodes
    print('{} {} {} {}'.format(node.name, macs['x1'], macs['n1'], macs['n2']))
