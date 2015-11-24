Discover
========

Cluster utility to automatically discover the MACs of a given set of nodes
based on the information available in the switches

Queries the switches using SNMP.

It is inspired by the lsslp and switchdiscovery utilities provided by xCAT.


Installation
------------

It is recommended to use virtualenv for development.

Installing dependencies: click, PyYAML, Jinja2, snimpy

    pip install click
    pip install PyYAML
    pip install Jinja2

**snimpy** needs libffi-dev and libsmi2-dev packages:
    sudo apt-get install libffi-dev
    sudo apt-get install libsmi2-dev
    pip install snimpy

Usage
-----
    discover learn --poweron c14-10
