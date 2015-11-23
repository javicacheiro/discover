# -*- coding: utf-8 -*-
"""CLI
   Implements the CLI interface using click
"""
from __future__ import print_function

import click
from . import config


@click.group(chain=True)
def cli():
    """Discover MAC addresses using SNMP and IPMI

    Example:

        discover learn
    """
    pass


@cli.command('learn')
@click.option('-c', '--confdir', default='', help="Conf directory")
def learn_cmd(confdir):
    if config.switches:
        click.echo(config.switches)
    else:
        click.echo("ERROR: Unable to load configuration files")


@cli.command('cobbler')
def cobbler_cmd():
    click.echo('Output of cobbler command')
