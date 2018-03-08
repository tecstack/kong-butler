# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: daisheng
# Email: shawntai.ds@gmail.com
#
# this module is a adapter to the KONG(api-gateway) administration restful api.
# in order to manage the 'comsumers' & 'credentials' of Kong.
#

class KongAdmin(object):
    """docstring for KongAdmin"""
    def __init__(self, kong_url=app.config['KONG_ADMIN_URL']):
        super(KongAdmin, self).__init__()
        self.arg = arg
        