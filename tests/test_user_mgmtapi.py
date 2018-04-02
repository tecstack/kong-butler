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


class TestApiUserList():
    '''
        Unit test for api: UserList
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
    def test_user_api_get_one_user(self):
        """
        [USER      ]user/user[get]: test get one user info
        """
        # login with correct username & password
        user = User.get_users(username=app.config['DEFAULT_ROOT_USERNAME'])[0]
        rv = self.app.get(
            '/api/v0.0/user/user?user_id='+user.user_id, 
            follow_redirects = True)
        assert app.config['DEFAULT_ROOT_USERNAME'] in rv.data
        eq_(rv.status_code, 200)

    @with_setup(setUp, tearDown)
    def test_user_api_add_user(self):
        """
        [USER      ]user/user[post]: test user add
        """
        # login with correct username & password
        users = User.get_users(username='tom1')
        if users:
            users[0].delete()
        role = Role.get_roles(role_name='root')[0]
        dict_data = dict(
                username='tom1', password=utils.hash_pass("tompass1"),
                role_id_list=[role.role_id])
        rv = self.app.post(
            '/api/v0.0/user/user', 
            data = json.dumps(dict_data),
            content_type = 'application/json',
            follow_redirects = True)
        print rv.data
        assert 'created' in rv.data
        eq_(rv.status_code, 200)

    @with_setup(setUp, tearDown)
    def test_user_api_put_user(self):
        """
        [USER      ]user/user[put]: test user put
        """
        # login with correct username & password
        users = User.get_users(username='tom')
        if users:
            user = users[0]
            user.update(username='tom', hashed_password=utils.hash_pass('tompass'))
        else:
            user = User(username='tom', hashed_password=utils.hash_pass('tompass'))
            user.save()
        dict_data = dict(password=utils.hash_pass("tompass1"))
        rv = self.app.put(
            '/api/v0.0/user/user?user_id='+user.user_id, 
            data = json.dumps(dict_data),
            content_type = 'application/json',
            follow_redirects = True)
        assert 'updated' in rv.data
        eq_(rv.status_code, 200)
