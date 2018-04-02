# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: daisheng
# Email: shawntai.ds@gmail.com
#
# This is the init file for the user package
# holding api & urls of the user module
#

from .mgmtapi import UserAPI
from .. import api, app

api.add_resource(
    UserAPI, '/api/' + app.config['API_VERSION'] + '/user/user',
    endpoint='user_ep')
