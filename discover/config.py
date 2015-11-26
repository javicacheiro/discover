# -*- coding: utf-8 -*-
"""Configuration module
   Implements the configuration related objects.
"""
from __future__ import print_function, with_statement
import os
import logging
import logging.config
import yaml
from jinja2 import Environment, FileSystemLoader


DEFAULT_CONF_DIRS = [os.path.expanduser('~/.discover'), '/etc/discover', './config']

SWFILE = 'switches.yml'
NODESFILE = 'nodes.yml'
LOGCONFFILE = 'logging.yml'
SETTINGSFILE = 'settings.yml'

switches = {}
nodes = {}
logconf = {}
settings = {}


class Config():
    """Configuration object

    Contains the switches, nodes and logging information
    """

    def __init__(self, confdir='', switches={}, nodes={}, logconf={}):
        if confdir:
            self.load(confdir)
        elif switches and nodes and logconf:
            self.switches = switches
            self.nodes = nodes
            self.logconf = logconf

    def load(self, confdir):
        """Load yaml configuration files from confdir
        Updates the values in the config from the yaml files stored in
        the given confdir.

        Two config files are needed:
            - switches.yml: info about the switches
            - nodes.yml: info about the nodes to scan
            - logging.yml: logging configuration

        :param confdir: the directory that contains the config files.
        """
        self.switches = self._load_file(SWFILE)
        self.nodes = self._load_file(NODESFILE)
        self.logconf = self._load_file(LOGCONFFILE)
        self.settings = self._load_file(SETTINGSFILE)

    def _load_file(self, filename):
        """Return a object representing the contents of a yaml file"""
        env = Environment(loader=FileSystemLoader(DEFAULT_CONF_DIRS, followlinks=True))
        template = env.get_template(filename)
        ymlfile = template.render(switches=switches, nodes=nodes)
        return yaml.load(ymlfile)

        #with open(filename, 'r') as ymlfile:
        #    return yaml.load(ymlfile)

    def __repr__(self):
        return '<{}(switches={}, nodes={}, logconf={})>'.format(
            self.__class__.__name__,
            dict.__repr__(self.switches),
            dict.__repr__(self.nodes),
            dict.__repr__(self.logconf)
        )


# Load config and expose it globally
for confdir in DEFAULT_CONF_DIRS:
    if os.path.exists(confdir):
        cfg = Config(confdir)
        logging.config.dictConfig(cfg.logconf)
        switches = cfg.switches
        nodes = cfg.nodes
        logconf = cfg.logconf
        settings = cfg.settings
        logging.debug('Configuration loaded from {}'.format(confdir))
