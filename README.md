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

Before installing **snimpy** you need gcc, libffi-dev and libsmi2-dev packages.

In Ubuntu 14.04:

    sudo apt-get install gcc
    sudo apt-get install libffi-dev
    sudo apt-get install libsmi2-dev

In RHEL7/CentOS/SL:

    yum install gcc
    yum install libffi-devel.x86_64
    yum install libsmi-devel.x86_64

After that you can install snimpy:

    pip install snimpy


    git clone https://github.com/javicacheiro/discover
    cd discover
    virtualenv venv
    . venv/bin/activate
    pip install --editable .

Usage
-----
    discover learn --poweron c14-10
