# -*- coding: utf-8 -*-
"""CLI
   Implements the CLI interface using click
"""
from __future__ import print_function

import json
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
@click.option('--poweron/--no-poweron', default=False, help="Poweron nodes for discovery")
@click.argument('nodename')
def learn_cmd(poweron, nodename):
    if nodename.lower() == 'all':
        discovery.discover_all()
        inventory.show()
    else:
        node = discovery.discover_node(nodename, poweron=poweron)
        inventory.print_node(node)


@cli.command('show')
def show_cmd():
    inventory.show()


@cli.command('cobbler')
def cobbler_cmd():
    click.echo('Output of cobbler command')
