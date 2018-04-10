# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: daisheng
# Email: shawntai.ds@gmail.com
#

import os
import logging

from flask import Flask

# Main flask object
app = Flask(__name__, instance_relative_config=True)

# Config File:
# use the instance/config.py to cover the default config object.
# u can put some instance settings into the instance/config.py

app.config.from_object('config')
if os.path.isfile(
        os.path.join(app.config['ABS_BASEDIR'], 'instance/config.py')):
    app.config.from_pyfile('config.py')

# Init .data, .tmp and .log Folder in root dir
if not os.path.exists(app.config['LOG_FOLDER']):
    os.mkdir(app.config['LOG_FOLDER'])
if 'DATA_FOLDER' in app.config:
    if not os.path.exists(app.config['DATA_FOLDER']):
        os.mkdir(app.config['DATA_FOLDER'])
if 'TMP_FOLDER' in app.config:
    if not os.path.exists(app.config['TMP_FOLDER']):
        os.mkdir(app.config['TMP_FOLDER'])

# Init The Api Obj
from flask.ext.restful import Api
api = Api(app)

from flask import make_response, json


@api.representation('application/json')
def responseJson(data, code, headers=None):
    resp = make_response(json.dumps(data), code)
    resp.headers.extend(headers or {})
    return resp


# Init The db Obj
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

import utils
# init the logger obj
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(utils.handler)

# Config for cross domain access
from flask.ext.cors import CORS
cors = CORS(app, allow_headers='*', expose_headers='Content-Disposition')

from flask.ext.cachecontrol import (
    FlaskCacheControl,
    cache,
    cache_for,
    dont_cache)
flask_cache_control = FlaskCacheControl()
flask_cache_control.init_app(app)


@app.route('/')
def hello_world():
    return 'Hello World!'

import user
