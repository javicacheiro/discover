# -*- coding: utf-8 -*-
"""CLI
   Implements the CLI interface using click
"""
from __future__ import print_function

import os
import click
from .config import Config

DEFAULT_CONF_DIRS = ['~/.discover', '/etc/discover', './config']

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
    if confdir:
        if os.path.exists(confdir):
            cfg = Config(confdir)
    else:
        for confdir in DEFAULT_CONF_DIRS:
            if os.path.exists(confdir):
                cfg = Config(confdir)
    if cfg:
        click.echo(cfg)
    else:
        click.echo("ERROR: Unable to load configuration files")


@cli.command('cobbler')
def cobbler_cmd():
    click.echo('Output of cobbler command')
