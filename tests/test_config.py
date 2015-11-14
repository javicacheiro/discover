# -*- coding: utf-8 -*-
from __future__ import print_function
from discover import config


def test_config():
    cfg = config.Config('../config/')
    print(cfg)
