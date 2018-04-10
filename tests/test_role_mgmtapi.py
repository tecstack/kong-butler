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


class TestApiUserMgmt():
    '''
        Unit test for api: UserMgmt
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
        [USER      ]user/role[get]: test get one role info
        """
        role = Role.get_roles(role_name=app.config['DEFAULT_ROOT_ROLENAME'])[0]
        rv = self.app.get(
            '/api/v0.0/user/role?role_id='+role.role_id, 
            follow_redirects = True)
        assert app.config['DEFAULT_ROOT_ROLENAME'] in rv.data
        eq_(rv.status_code, 200)

    @patch.object(consumer_inf, 'add', Mock())
    @patch.object(group_inf, 'set_groups2consumer', Mock())
    @patch.object(Group, 'usernames', Mock())
    @patch.object(Group, 'api_ids', Mock())
    @with_setup(setUp, tearDown)
    def test_role_api_add_role(self):
        """
        [USER      ]user/role[post]: test role add
        """
        roles = Role.get_roles(role_name='role1')
        if roles:
            roles[0].delete()
        user = User.get_users(username=app.config['DEFAULT_ROOT_USERNAME'])[0]
        api_ids = Api.list_api_ids()
        dict_data = dict(
                role_name='role1', user_ids=[user.user_id], api_ids=api_ids)
        rv = self.app.post(
            '/api/v0.0/user/role', 
            data = json.dumps(dict_data),
            content_type = 'application/json',
            follow_redirects = True)
        assert 'created' in rv.data
        eq_(rv.status_code, 200)#

    @patch.object(consumer_inf, 'add', Mock())
    @patch.object(group_inf, 'set_groups2consumer', Mock())
    @patch.object(Group, 'usernames', Mock())
    @patch.object(Group, 'api_ids', Mock())
    @with_setup(setUp, tearDown)
    def test_role_api_put_role(self):
        """
        [USER      ]user/role[put]: test role put
        """
        roles = Role.get_roles(role_name='role1')
        if roles:
            role = roles[0]
        else:
            role = Role(role_name='role1')
            role.save()
        user = User.get_users(username=app.config['DEFAULT_ROOT_USERNAME'])[0]
        dict_data = dict(user_ids=[user.user_id])
        rv = self.app.put(
            '/api/v0.0/user/role?role_id='+role.role_id, 
            data = json.dumps(dict_data),
            content_type = 'application/json',
            follow_redirects = True)
        print rv.data
        assert 'updated' in rv.data
        eq_(rv.status_code, 200)
