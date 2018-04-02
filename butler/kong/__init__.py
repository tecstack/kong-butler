# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: daisheng
# Email: shawntai.ds@gmail.com

"""Top-level package for Python Kong Management."""

from butler import app

__version__ = '0.12.1'
_KONGADM_URL = app.config['KONGADM_URL']
_KONGADM_APIKEY = app.config['KONGADM_APIKEY']
_KONGADM_BASICAUTH = None
_USE_SESSION = True
