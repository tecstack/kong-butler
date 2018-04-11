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
from butler.kong.client import Client, Session, request
from butler.kong.baseinf import *
from butler import app
from mock import Mock, patch


class TestClient():
    """
    test butler.kong.client
    """
    # establish db
    def setUp(self):
        app.testing = True

        self.app = app.test_client()

    # drop db
    def tearDown(self):
        pass

    @staticmethod
    def mock_resp(status_code=200, encoding='utf-8', content=dict(message='test results')):
        resp_dict = dict(
            status_code=status_code,
            encoding=encoding,
            content=json.dumps(content)
            )
        return Mock(return_value=Options(**resp_dict))

    @with_setup(setUp, tearDown)
    def test_kong_client(self):
        """
        [KONG      ]butler.kong.client
        """
        with patch.object(Session, 'request', self.mock_resp()):
            basic_auth = dict(username='username', password='password')
            kong_client = Client('http://testip.com', basic_auth=basic_auth, use_session=True)
            data = kong_client.execute('GET', 'testpath/', None)
            kong_client.destroy()
            assert 'message' in data#

    @with_setup(setUp, tearDown)
    def test_kong_baseinf_nodeinf(self):
        """
        [KONG      ]butler.kong.baseinf.nodeinf
        """
        content = dict(version='123')
        with patch.object(Session, 'request', self.mock_resp(content=content)):
            nodeinf = NodeInf()
            data = nodeinf.retrieve_info()
            assert 'version' in data
            data = nodeinf.retrieve_status()
            assert 'version' in data

    @with_setup(setUp, tearDown)
    def test_kong_baseinf_consumerinf(self):
        """
        [KONG      ]butler.kong.baseinf.consumerinf
        """
        content = dict(id='123')
        with patch.object(Session, 'request', self.mock_resp(content=content)):
            cinf = ConsumerInf()
            data = cinf.retrieve('123')
            assert '123' in data['id']

    @with_setup(setUp, tearDown)
    def test_kong_baseinf_consumerinf(self):
        """
        [KONG      ]butler.kong.baseinf.consumerinf
        """
        cinf = ConsumerInf()
        content = dict(id='123')
        with patch.object(Session, 'request', self.mock_resp(content=content)):
            data = cinf.retrieve('123')
            assert '123' in data['id']
            with patch.object(ConsumerInf, 'retrieve', Mock(return_value=None)):
                data = cinf.add('tom')
                assert '123' in data
            data = cinf.delete('123')
            assert '123' in data['id']

        with patch.object(Session, 'request', self.mock_resp(content=dict())):
            with patch.object(ConsumerInf, 'retrieve', Mock(return_value=None)):
                data = cinf.add('tom')
                assert data is None

    @with_setup(setUp, tearDown)
    def test_kong_baseinf_apiinf(self):
        """
        [KONG      ]butler.kong.baseinf.apiinf
        """
        content = dict(id='123')
        with patch.object(Session, 'request', self.mock_resp(content=content)):
            ainf = ApiInf()
            data = ainf.retrieve('123')
            assert '123' in data['id']
        content = dict(total=2, data=['123', '234'])
        with patch.object(Session, 'request', self.mock_resp(content=content)):
            ainf = ApiInf()
            total, data = ainf.list()
            assert '123' in data

    @with_setup(setUp, tearDown)
    def test_kong_baseinf_plugininf(self):
        """
        [KONG      ]butler.kong.baseinf.plugininf
        """
        content = dict(id='123')
        with patch.object(Session, 'request', self.mock_resp(content=content)):
            pinf = PluginInf()
            data = pinf.retrieve('123')
            assert '123' in data['id']

        content = dict(id='123', name='123', enabled=True, api_id='123', config='123')
        with patch.object(Session, 'request', self.mock_resp(content=content)):
            pinf = PluginInf()
            id, name, enabled, api_id, config = pinf.add('123')
            assert '123' in id
            data = pinf.update(plugin_id='123', api_name_or_id='123', plugin_name='acl')
            assert '123' in data['id']
        content = dict(total=1, data=['123'])
        with patch.object(Session, 'request', self.mock_resp(content=content)):
            pinf = PluginInf()
            num, data = pinf.list()
            assert '123' in data#

    @with_setup(setUp, tearDown)
    def test_kong_baseinf_aclinf(self):
        """
        [KONG      ]butler.kong.baseinf.aclplugininf
        """
        content = dict(id='123')
        with patch.object(Session, 'request', self.mock_resp(content=content)):
            aclinf = AclPluginInf()
            data = aclinf._retrieve('123')
            assert '123' in data['id']
        content = dict(total=1, data=[dict(id='123')])
        with patch.object(Session, 'request', self.mock_resp(content=content)):
            data = aclinf.get_acllist('123')
            assert 'whitelist' in data
            data = aclinf.set_acllist(api_id='123', whitelist=['123'], blacklist=['123'])

    @with_setup(setUp, tearDown)
    def test_kong_baseinf_jwtinf(self):
        """
        [KONG      ]butler.kong.baseinf.jwtplugininf
        """
        content = dict(id='123')
        with patch.object(Session, 'request', self.mock_resp(content=content)):
            jwtinf = JwtPluginInf('123')
            data = jwtinf.retrieve('123')
            assert '123' in data['id']

    @with_setup(setUp, tearDown)
    def test_kong_baseinf_groupinf(self):
        """
        [KONG      ]butler.kong.baseinf.groupinf
        """
        content = dict(data=['123'])
        with patch.object(Session, 'request', self.mock_resp(content=content)):
            ginf = GroupInf()
            data = ginf.retrieve('123', '123')
            assert '123' in data

#    @with_setup(setUp, tearDown)
#    def test_kong_baseinf_jwtcredinf(self):
#        """
#        [KONG      ]butler.kong.baseinf.jwtcredinf
#        """
#        content = dict(id=['123'])
#        with patch.object(Session, 'request', self.mock_resp(content=content)):
#            jinf = JwtCredInf('123')
#            data = jinf.retrieve()
#            assert '123' in data['id']
#            content = dict(total=1, data=[dict(id='123')])
#            with patch.object(Session, 'request', self.mock_resp(content=content)):
#                data = jinf.add()

    @with_setup(setUp, tearDown)
    def test_kong_baseinf_token(self):
        """
        [KONG      ]butler.kong.baseinf.token
        """
        token = JwtCredInf.token_gen(key='testkey', secret='testsecret')
        payload = JwtCredInf.token_decode(token=token, secret='testsecret')
        assert 'testkey' in payload['iss']
