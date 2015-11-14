# -*- coding: utf-8 -*-
import re
from discover import cli


def test_help(runner):
    result = runner.invoke(cli, ['--help'])
    assert not result.exception
    assert re.search(r'Discover MAC addresses using SNMP and IPMI', result.output) is not None


def test_learn(runner):
    result = runner.invoke(cli, ['learn'])
    assert not result.exception
    assert result.output == 'Output of learn command'
