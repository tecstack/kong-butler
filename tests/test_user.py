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
from bulter import app, db


class TestApiUserList():
    '''
        Unit test for api: UserList
    '''
    # establish db
    def setUp(self):
        app.testing = True
        db.create_all()
        print 'Data imported'

        self.app = app.test_client()

    # drop db
    def tearDown(self):
        pass

    @with_setup(setUp, tearDown)
    def test_user_api_get_one_user(self):
        """
        [USER      ]user/user[get]: test get one user info
        """
        pass
