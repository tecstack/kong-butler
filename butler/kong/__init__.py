# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: daisheng
# Email: shawntai.ds@gmail.com

"""Top-level package for Python Kong Management."""

from butler import app

__version__ = '0.12.1'
_KONGADM_URL = app.config['KONGADM_URL']
if 'KONGADM_APIKEY' in app.config:
    _KONGADM_APIKEY = app.config['KONGADM_APIKEY']
else:
    _KONGADM_APIKEY = None
if 'KONGADM_BASICAUTH_USERNAME' in app.config and 'KONGADM_BASICAUTH_PASSWORD' in app.config:
    _KONGADM_BASICAUTH = dict(
        username=app.config['KONGADM_BASICAUTH_USERNAME'],
        password=app.config['KONGADM_BASICAUTH_PASSWORD'])
else:
    _KONGADM_BASICAUTH = None
_USE_SESSION = True
