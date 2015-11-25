# -*- coding: utf-8 -*-
"""Discovery module
   Implements the discovery of MAC addresses.
"""
from __future__ import print_function, with_statement
import logging
import time
from .node import Node
from . import switch
from . import config
from . import inventory

# Number of retries
RETRIES = 4
# Time between retries
DELAY = 60

logger = logging.getLogger(__name__)


class DiscoveryFailedError(Exception):
    """Unable to complete discovery"""
    pass


class MultipleMacError(DiscoveryFailedError):
    """More than one MAC found"""
    pass


class ReachedRetryCount(DiscoveryFailedError):
    """Number of retries reached for node discovery"""
    pass


def discover_all(parallel=True, poweron=True, poweroff=False):
    """Discover all nodes given in the configuration"""
    nodes = []

    # If we have to do sequential discovery
    if not parallel:
        for nodename in config.nodes:
            node = discover_node(nodename, poweron=poweron)
            nodes.append(node)
        return nodes

    # In other case let's do it in parallel
    for nodename in config.nodes:
        node = discover_node(nodename, poweron=False)
        nodes.append(node)
    for node in nodes:
        if node.has_missing_macs():
            if node.is_off():
                # Temporarily activating PXE helps in the discovery
                logger.info('Temporarily activating PXE on node {}'.format(node.name))
                node.activate_pxe()
                logger.info('Powering on node {}'.format(node.name))
                node.power_on()
            else:
                if poweroff:
                    logger.info('Powering off node {}'.format(node.name))
                    node.power_off()
                    # Temporarily activating PXE helps in the discovery
                    logger.info('Temporarily activating PXE on node {}'.format(node.name))
                    node.activate_pxe()
                    logger.info('Powering on node {}'.format(node.name))
                    node.power_on()
                else:
                    logger.warn(
                        '{} with missing MACs is already on'.format(node.name))
                    logger.warn(
                        'CLI is run without poweroff option so you should reboot the node manually')
    for attempt in range(RETRIES):
        logger.info('Attempt {}/{}'.format(attempt+1, RETRIES))
        logger.debug('Waiting {} seconds to retry'.format(DELAY))
        time.sleep(DELAY)
        finished = True
        for node in nodes:
            if node.has_missing_macs():
                _query_switches(node)
            if node.has_missing_macs():
                finished = False
        if finished:
            for node in nodes:
                inventory.save(node)
            return nodes

    for node in nodes:
        inventory.save(node)

    raise ReachedRetryCount('Unable to discover all nodes')


def discover_node(nodename, poweron=True, poweroff=False):
    """Find the MAC addresses of a given node"""
    try:
        node = inventory.load(nodename)
    except inventory.NodeNotFoundError:
        nodecfg = config.nodes[nodename]
        node = Node(nodename, nodecfg['switchports'],
                    nodecfg['bmc']['address'], nodecfg['bmc']['user'],
                    nodecfg['bmc']['password'])

    # Nothing to do if it already has all the macs discovered from inventory
    if node.has_all_macs():
        return node

    # First try: we retrieve what the switches already now
    _query_switches(node)

    if poweron:
        # Second try: we turn on the node and retry
        if node.has_missing_macs():
            if node.is_off():
                # Temporarily activating PXE helps in the discovery
                logger.info('Temporarily activating PXE on node {}'.format(node.name))
                node.activate_pxe()
                logger.info('Powering on node {}'.format(node.name))
                node.power_on()
            else:
                logger.warn('Node {} was already on'.format(node.name))
                if poweroff:
                    logger.info('Powering off node {}'.format(node.name))
                    node.power_off()
                    # Temporarily activating PXE helps in the discovery
                    logger.info('Temporarily activating PXE on node {}'.format(node.name))
                    node.activate_pxe()
                    logger.info('Powering on node {}'.format(node.name))
                    node.power_on()
                else:
                    logger.warn(
                        '{} with missing MACs is already on'.format(node.name))
                    logger.warn(
                        'CLI is run without poweroff option so you should reboot the node manually')
            for attempt in range(RETRIES):
                logger.info('Attempt {}/{}'.format(attempt+1, RETRIES))
                if node.has_missing_macs():
                    logger.debug('Waiting {} seconds to retry'.format(DELAY))
                    time.sleep(DELAY)
                else:
                    inventory.save(node)
                    return node
                _query_switches(node)
        # Recap
        if node.has_all_macs():
            inventory.save(node)
            return node
        else:
            logger.warn(
                'Unable to find all MACs for node {} after {} retries'
                .format(node.name, RETRIES))
            logger.info('MACs found: {}'.format(node.switchports))
            inventory.save(node)
            return node
    else:
        # If poweron=False just return what we found until now
        inventory.save(node)
        logger.warn('Unable to discover all MACs of {}'.format(node.name))
        return node


def _query_switches(node):
    """Query switches for the MACs of the given node"""
    for swname, swopts in node.switchports.items():
        if 'mac' not in swopts:
            macs = switch.query(swname, swopts['port'], swopts['vlan'])
            if len(macs) == 1:
                node.add_mac(swname, macs[0])
            elif len(macs) > 1:
                logger.error('Found {} MACs for node {} on switch {}'.format(
                    len(macs), node.name, swname))
                raise MultipleMacError(
                    'Found more than one MAC in the given port')
            else:
                logger.debug('MAC not found for node {} on switch {}'.format(
                    node.name, swname))
