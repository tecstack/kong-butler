#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Author: daisheng
# Email: shawntai.ds@gmail.com
#
# This is the config file of global package of promise-butler.
# You can create your own instance/config.py which will cover this file.
# Also instance/nosetests_config.py has higher priority when testing.
#
import os
import logging

"""
    common
"""
API_VERSION = 'v0.0'
# ENVIRONMENTS = ('qa', 'online')
ENVIRONMENTS = ('qa', )
ABS_BASEDIR = os.path.split(os.path.realpath(__file__))[0]
BASEDIR = os.path.abspath(os.path.dirname('..'))
DATA_FOLDER = os.path.join(BASEDIR, '.data')
LOG_FOLDER = os.path.join(BASEDIR, '.log')
LOGGER_FILE = os.path.join(LOG_FOLDER, 'debug.log')
TMP_FOLDER = os.path.join(BASEDIR, '.tmp')
CA_FOLDER = os.path.join(BASEDIR, '.ca')
UPLOAD_FOLDER = os.path.join(DATA_FOLDER, 'upload')
BACKUP_FOLDER = os.path.join(DATA_FOLDER, 'backup')
DEFAULT_LOGLEVEL = logging.DEBUG


"""
    database
"""
# database access string setting, by default we use mysql
# for common using
SQLALCHEMY_DATABASE_URI = 'mysql://name:pass@yourmysql/butler'
SQLALCHEMY_POOL_RECYCLE = 5
PROPAGATE_EXCEPTIONS = True

KONGADM_URL = 'http://testurl.com'
KONGADM_APIKEY = None
KONGADM_BASICAUTH_USERNAME = None
KONGADM_BASICAUTH_PASSWORD = None

DEFAULT_ROOT_USERNAME = 'admin'
DEFAULT_ROOT_PASSWORD = 'admin'
DEFAULT_ROOT_ROLENAME = 'root'

# encryption keys
SECRET_KEY = 'your SECRET_KEY'
# salt used by token generation
AUTH_SALT = 'your AUTH SALT'
# salt used by password md5 hash
PSW_SALT = 'your PSW SALT'
