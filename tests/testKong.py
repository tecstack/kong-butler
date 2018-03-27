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
from bulter.kong.baseinf import *
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
    def mock_resp(status_code=200, encoding='utf-8', content=dict(message='test results')):
        resp_dict = dict(
            status_code=status_code,
            encoding=encoding,
            content=json.dumps(content)
            )
        return Mock(return_value=Options(**resp_dict))

    @with_setup(set_up, tear_down)
    def test_kong_client(self):
        """
        [KONG      ]bulter.kong.client
        """
        # test basic_auth client
        with patch.object(requests, 'request', self.mock_resp()):
            basic_auth = dict(username='username', password='password')
            kong_client = Client('http://testip.com', basic_auth=basic_auth)
            data = kong_client.execute('GET', 'testpath/', None)
            kong_client.destroy()
            assert 'message' in data
        with patch.object(requests.Session, 'request', self.mock_resp()):
            basic_auth = dict(username='username', password='password')
            kong_client = Client('http://testip.com', basic_auth=basic_auth, use_session=True)
            data = kong_client.execute('GET', 'testpath/', None)
            kong_client.destroy()
            assert 'message' in data

    @with_setup(set_up, tear_down)
    def test_kong_baseinf_nodeinf(self):
        """
        [KONG      ]bulter.kong.baseinf.nodeinf
        """
        content = dict(version='123')
        with patch.object(requests, 'request', self.mock_resp(content=content)):
            kong_client = Client('http://testip.com')
            nodeinf = NodeInf(kong_client)
            data = nodeinf.retrieve_info()
            assert 'version' in data
            data = nodeinf.retrieve_status()
            assert 'version' in data

    @with_setup(set_up, tear_down)
    def test_kong_baseinf_consumerinf(self):
        """
        [KONG      ]bulter.kong.baseinf.consumerinf
        """
        content = dict(id='123')
        with patch.object(requests, 'request', self.mock_resp(content=content)):
            kong_client = Client('http://testip.com')
            cinf = ConsumerInf(kong_client)
            data = cinf.retrieve('123')
            assert '123' in data['id']

    @with_setup(set_up, tear_down)
    def test_kong_baseinf_consumerinf(self):
        """
        [KONG      ]bulter.kong.baseinf.consumerinf
        """
        kong_client = Client('http://testip.com')
        cinf = ConsumerInf(kong_client)
        content = dict(id='123')
        with patch.object(requests, 'request', self.mock_resp(content=content)):
            data = cinf.retrieve('123')
            assert '123' in data['id']
            with patch.object(ConsumerInf, 'retrieve', Mock(return_value=None)):
                data = cinf.add('tom')
                assert '123' in data
            data = cinf.delete('123')
            assert '123' in data['id']

        with patch.object(requests, 'request', self.mock_resp(content=dict())):
            with patch.object(ConsumerInf, 'retrieve', Mock(return_value=None)):
                data = cinf.add('tom')
                assert data is None

    @with_setup(set_up, tear_down)
    def test_kong_baseinf_apiinf(self):
        """
        [KONG      ]bulter.kong.baseinf.apiinf
        """
        content = dict(id='123')
        with patch.object(requests, 'request', self.mock_resp(content=content)):
            kong_client = Client('http://testip.com')
            ainf = ApiInf(kong_client)
            data = ainf.retrieve('123')
            assert '123' in data['id']

    @with_setup(set_up, tear_down)
    def test_kong_baseinf_plugininf(self):
        """
        [KONG      ]bulter.kong.baseinf.plugininf
        """
        content = dict(id='123')
        with patch.object(requests, 'request', self.mock_resp(content=content)):
            kong_client = Client('http://testip.com')
            pinf = PluginInf(kong_client)
            data = pinf.retrieve('123')
            assert '123' in data['id']

        content = dict(id='123', name='123', enabled=True, api_id='123', config='123')
        with patch.object(requests, 'request', self.mock_resp(content=content)):
            kong_client = Client('http://testip.com')
            pinf = PluginInf(kong_client)
            id, name, enabled, api_id, config = pinf.add('123')
            assert '123' in id
            data = pinf.update(plugin_id='123', api_name_or_id='123', plugin_name='acl')
            assert '123' in data['id']

        content = dict(total=1, data=['123'])
        with patch.object(requests, 'request', self.mock_resp(content=content)):
            kong_client = Client('http://testip.com')
            pinf = PluginInf(kong_client)
            num, data = pinf.list()
            assert '123' in data

    @with_setup(set_up, tear_down)
    def test_kong_baseinf_aclinf(self):
        """
        [KONG      ]bulter.kong.baseinf.aclplugininf
        """
        content = dict(id='123')
        with patch.object(requests, 'request', self.mock_resp(content=content)):
            kong_client = Client('http://testip.com')
            aclinf = AclPluginInf(kong_client, '123')
            data = aclinf.retrieve('123')
            assert '123' in data['id']
        content = dict(total=1, data=[dict(id='123')])
        with patch.object(requests, 'request', self.mock_resp(content=content)):
            data = aclinf.get_acllist()
            assert 'whitelist' in data
            data = aclinf.set_acllist(whitelist=['123'], blacklist=['123'])

    @with_setup(set_up, tear_down)
    def test_kong_baseinf_jwtinf(self):
        """
        [KONG      ]bulter.kong.baseinf.jwtplugininf
        """
        content = dict(id='123')
        with patch.object(requests, 'request', self.mock_resp(content=content)):
            kong_client = Client('http://testip.com')
            jwtinf = JwtPluginInf(kong_client, '123')
            data = jwtinf.retrieve('123')
            assert '123' in data['id']

    @with_setup(set_up, tear_down)
    def test_kong_baseinf_groupinf(self):
        """
        [KONG      ]bulter.kong.baseinf.groupinf
        """
        content = dict(data=['123'])
        with patch.object(requests, 'request', self.mock_resp(content=content)):
            kong_client = Client('http://testip.com')
            ginf = GroupInf(kong_client)
            data = ginf.retrieve('123', '123')
            assert '123' in data

    @with_setup(set_up, tear_down)
    def test_kong_baseinf_jwtcredinf(self):
        """
        [KONG      ]bulter.kong.baseinf.jwtcredinf
        """
        content = dict(id=['123'])
        with patch.object(requests, 'request', self.mock_resp(content=content)):
            kong_client = Client('http://testip.com')
            jinf = JwtCredInf(kong_client, '123')
            data = jinf.retrieve('123')
            assert '123' in data['id']
            content = dict(total=1, data=[dict(id='123')])
            with patch.object(requests, 'request', self.mock_resp(content=content)):
                data = jinf.add()

    @with_setup(set_up, tear_down)
    def test_kong_baseinf_token(self):
        """
        [KONG      ]bulter.kong.baseinf.token
        """
        token = JwtCredInf.token_gen(key='testkey', secret='testsecret')
        payload = JwtCredInf.token_decode(token=token, secret='testsecret')
        assert 'testkey' in payload['iss']
