# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#

import sys, json
sys.path.append('..')

from utils import *
import json
import os
from bulter.kong.client import Client, requests
from mock import Mock, patch


class TestClient():
    """
    test bulter.kong.client
    """
    # establish db
    def set_up(self):
        app.testing = True
        db.create_all()
        print 'Data imported'

        self.app = app.test_client()

    # drop db
    def tear_down(self):
        pass

    @staticmethod
    def setup_resp(status_code=200, encoding='utf-8', content='{"message":"test results"}\n'):
        resp_dict = dict(
            status_code=status_code,
            encoding=encoding,
            content=content
            )
        return Options(**resp_dict)

    @with_setup(set_up, tear_down)
    def test_kong_client(self):
        """
        [KONG      ]bulter.kong.client
        """
        # test basic_auth client
        resp = Mock(return_value=self.setup_resp())
        with patch.object(requests, 'request', resp):
            basic_auth = dict(username='username', password='password')
            kong_client = Client('http://testip.com', basic_auth=basic_auth)
            data = kong_client.execute('GET', 'testpath/', None)
            kong_client.destroy()
            assert 'message' in data
        with patch.object(requests.Session, 'request', resp):
            basic_auth = dict(username='username', password='password')
            kong_client = Client('http://testip.com', basic_auth=basic_auth, use_session=True)
            data = kong_client.execute('GET', 'testpath/', None)
            kong_client.destroy()
            assert 'message' in data
