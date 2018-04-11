# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: daisheng
# Email: shawntai.ds@gmail.com
#
# This is the init file for the user package
# holding api & urls of the user module
#

from .auth import TokenAPI, LoginAPI
from .. import api, app

api.add_resource(LoginAPI, '/api/%s/auth' % app.config['API_VERSION'], endpoint='login_ep')
api.add_resource(TokenAPI, '/api/%s/token' % app.config['API_VERSION'], endpoint='token_ep')
