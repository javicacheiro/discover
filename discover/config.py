# -*- coding: utf-8 -*-
"""Configuration module
   Implements the configuration related objects.
"""
from __future__ import print_function, with_statement
import os
import yaml

DEFAULT_CONF_DIRS = [os.path.expanduser('~/.discover'), '/etc/discover', './config']
switches = {}
nodes = {}


class Config():
    """Configuration object

    Contains the switches and nodes information
    """

    def __init__(self, confdir='', switches={}, nodes={}):
        if confdir:
            self.load(confdir)
        elif switches and nodes:
            self.switches = switches
            self.nodes = nodes

    def load(self, confdir):
        """Load yaml configuration files from confdir
        Updates the values in the config from the yaml files stored in
        the given confdir.

        Two config files are needed:
            - switches.yml: info about the switches
            - nodes.yml: info about the nodes to scan

        :param confdir: the directory that contains the config files.
        """
        swfile = os.path.join(confdir, 'switches.yml')
        nodesfile = os.path.join(confdir, 'nodes.yml')
        self.switches = self._load_file(swfile)
        self.nodes = self._load_file(nodesfile)

    def _load_file(self, filename):
        """Return a object representing the contents of a yaml file"""
        with open(filename, 'r') as ymlfile:
            return yaml.load(ymlfile)

    def __repr__(self):
        return '<%s(switches=%s, nodes=%s)>' % (self.__class__.__name__,
            dict.__repr__(self.switches),
            dict.__repr__(self.nodes)
        )


# Load config and expose it globally
for confdir in DEFAULT_CONF_DIRS:
    if os.path.exists(confdir):
        cfg = Config(confdir)
        switches = cfg.switches
        nodes = cfg.nodes
