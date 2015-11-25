# -*- coding: utf-8 -*-
"""CLI
   Implements the CLI interface using click
"""
from __future__ import print_function

import click
from . import discovery
from . import inventory


@click.group(chain=True)
def cli():
    """Discover MAC addresses using SNMP and IPMI

    Example:

        discover learn
    """
    pass


@cli.command('learn')
@click.option('--poweron/--no-poweron', default=True, help="Poweron nodes for discovery")
@click.option('--poweroff/--no-poweroff', default=False, help="Poweroff nodes for discovery")
@click.option('--parallel/--no-parallel', default=True, help="Discover in parallel/sequential way")
@click.option('--intelligent/--no-intelligent', default=True, help="Intelligent mode")
@click.argument('nodename')
def learn_cmd(poweron, poweroff, parallel, intelligent, nodename):
    # The special keyword 'all' means to discover all nodes
    if nodename.lower() == 'all':
        try:
            discovery.discover_all(parallel=parallel, poweron=poweron, poweroff=poweroff)
        except discovery.ReachedRetryCount:
            if intelligent:
                # In intelligent mode: Let's try again in sequential mode
                try:
                    discovery.discover_all(
                        parallel=False, poweron=poweron, poweroff=poweroff)
                except discovery.ReachedRetryCount:
                    click.echo('Unable to discover all nodes using intelligent mode')
        inventory.show()
    else:
        try:
            discovery.discover_node(nodename, poweron)
        except discovery.DiscoveryFailedError as e:
            click.echo('Discovery failed: ' + str(e))
        inventory.show(nodename)


@cli.command('show')
def show_cmd():
    inventory.show()


@cli.command('cobbler')
def cobbler_cmd():
    click.echo('Output of cobbler command')
