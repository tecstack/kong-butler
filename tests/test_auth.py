# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is
# autotest for the Auth API of user package

import sys, json
sys.path.append('..')

from nose.tools import *
import json
import os

from sqlite3 import dbapi2 as sqlite3

from butler.user.mgmtapi import *
from butler import app, db
import utils as test_utils
from butler.user import utils
from mock import Mock, patch
from butler.user.models import User, Role
from butler.kong.kongadm import group_inf, consumer_inf, api_inf, aclplugin_inf, Group


class TestApiAuth():
    '''
        Unit test for api: Auth
    '''
    # establish db
    def setUp(self):
        app.testing = True
        db.create_all()
        test_utils.init_user_data()
        print 'Data imported'
        self.app = app.test_client()

    # drop db
    def tearDown(self):
        pass

    @with_setup(setUp, tearDown)
    def test_role_api_get_one_role(self):
        """
        [AUTH      ]auth[post]: test login
        """
