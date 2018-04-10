# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: daisheng
# Email: shawntai.ds@gmail.com
#
# This is the init file for the user package
# holding api & urls of the user module
#

from .mgmtapi import UserAPI, RoleAPI, ApiAPI
from .. import api, app

api.add_resource(UserAPI, '/api/%s/user/user' % app.config['API_VERSION'], endpoint='user_ep')
api.add_resource(RoleAPI, '/api/%s/user/role' % app.config['API_VERSION'], endpoint='role_ep')
api.add_resource(ApiAPI, '/api/%s/user/api' % app.config['API_VERSION'], endpoint='api_ep')
