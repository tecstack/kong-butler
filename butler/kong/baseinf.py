# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: daisheng
# Email: shawntai.ds@gmail.com


import utils
from client import Client
from exceptions import *
import jwt
import datetime
from jwt.exceptions import InvalidSignatureError
from ..kong import _KONGADM_URL, _KONGADM_APIKEY, _KONGADM_BASICAUTH, _USE_SESSION

TOKEN_EXPDURATION = 3600
TOKEN_ALGORITHM = 'HS256'

logger = utils.logger


client = Client(base_url=_KONGADM_URL, apikey=_KONGADM_APIKEY, basic_auth=_KONGADM_BASICAUTH,
                use_session=_USE_SESSION)


class NodeInf(object):
    """docstring for KongNode"""
    def __init__(self, client=client):
        super(NodeInf, self).__init__()
        self._client = client

    def retrieve_info(self):
        return self._client.execute('GET', '')

    def retrieve_status(self):
        return self._client.execute('GET', 'status')


class ConsumerInf(object):
    """docstring for Consumer"""
    def __init__(self, client=client):
        super(ConsumerInf, self).__init__()
        self._client = client

    def add(self, username):
        """
        :return: id of consumer
        """
        consumer_id = self.retrieve(username)
        if consumer_id is not None:
            # raise UsernameDuplicateError('username<%s> duplicated.' % username)
            return consumer_id

        req_params = dict(username=username)
        if req_params:
            resp = self._client.execute('POST', 'consumers', req_params)
            try:
                return resp['id']
            except KeyError as e:
                logger.error('create consumer faild: %s' % e)
                return None
        else:
            logger.warning('need username or custom_id to create consumer.')
            return None

    def retrieve(self, username_or_id):
        """
        :return: consumer info: username, custom_id, id, create_time
        """
        try:
            return self._client.execute('GET', 'consumers/%s' % username_or_id)
        except ResourceNotFoundError:
            return None

    def list(self):
        """
        :return: total_num, consumers list
        """
        body = self._client.execute('GET', 'consumers')
        return body['total'], body['data']

    def update(self, username, tar_username_or_id):
        """
        :return:
        """
        req_params = dict(username=username)
        return self._client.execute('PATCH', 'consumers/%s' % tar_username_or_id, req_params)

    def delete(self, username_or_id):
        """
        :return:
        """
        try:
            return self._client.execute('DELETE', 'consumers/%s' % username_or_id)
        except ResourceNotFoundError:
            logger.info('username_or_id<%s> not found when deleting consumer.' % username_or_id)
            return None


class ApiInf(object):
    """docstring for api"""
    def __init__(self, client=client):
        super(ApiInf, self).__init__()
        self._client = client

    def add(self):
        pass

    def retrieve(self, name_or_id):
        """
        :return: api info
        """
        try:
            return self._client.execute('GET', 'apis/%s' % name_or_id)
        except ResourceNotFoundError:
            return None

    def list(self):
        """
        :return: total_num, api list
        """
        body = self._client.execute('GET', 'apis')
        return body['total'], body['data']


class PluginInf(object):
    """docstring for Plugin"""
    def __init__(self, client=client):
        super(PluginInf, self).__init__()
        self._client = client

    def add(self, plugin_name, api_id=None, consumer_id=None, **config_params):
        """

        :return:
        """
        if api_id is not None:
            path = 'apis/%s/plugins/' % api_id
        else:
            path = '/plugins'

        req_params = dict(name=plugin_name)
        if consumer_id is not None:
            req_params['consumer_id'] = consumer_id
        if config_params:
            for config_key in config_params:
                req_params['config.%s' % config_key] = config_params[config_key]

        body = self._client.execute('POST', path, req_params)
        return body['id'], body['name'], body['enabled'], body['api_id'], body['config']

    def retrieve(self, plugin_id):
        """

        :return: plugin info
        """
        return self._client.execute('GET', 'plugins/%s' % plugin_id)

    def list(self, plugin_id=None, plugin_name=None, api_id=None, consumer_id=None, size=100,
             offset=None):
        """

        :return: total num, plugin list
        """
        req_params = dict()
        if plugin_id is not None:
            req_params['id'] = plugin_id
        if plugin_name is not None:
            req_params['name'] = plugin_name
        if api_id is not None:
            req_params['api_id'] = api_id
        if consumer_id:
            req_params['consumer_id'] = consumer_id
        if size:
            req_params['size'] = size
        if offset:
            req_params['offset'] = offset

        body = self._client.execute('GET', 'plugins', req_params)
        return body['total'], body['data']

    def list_per_api(self, api_id):
        """

        :return: total num, plugin list
        """
        body = self._client.execute('GET', 'apis/%s/plugins' % api_id)
        return body['total'], body['data']

    def delete(self, plugin_id, api_name_or_id):
        """

        :return:
        """
        return self._client.execute(
            'DELETE', 'apis/%s/plugins/%s' % (api_name_or_id, plugin_id))

    def update(self, plugin_id, api_name_or_id, plugin_name, consumer_id=None, **config_params):
        """

        :return:
        """
        req_params = dict(name=plugin_name)
        if consumer_id:
            req_params['consumer_id'] = consumer_id
        if config_params:
            for config_key in config_params:
                req_params['config.%s' % config_key] = config_params[config_key]
        return self._client.execute(
            'PATCH', 'apis/%s/plugins/%s' % (api_name_or_id, plugin_id), req_params)


class AclPluginInf(PluginInf):
    """docstring for AclPluginInf"""
    def __init__(self, api_id, client=client):
        super(AclPluginInf, self).__init__(client)
        self._plugin_name = 'acl'
        self._api_id = api_id

    def _add(self, whitelist=None, blacklist=None):
        config_params = dict()
        if whitelist is not None:
            config_params['whitelist'] = whitelist
        if blacklist is not None:
            config_params['blacklist'] = blacklist
        return super(AclPluginInf, self).add(
            plugin_name=self._plugin_name, api_id=self._api_id, **config_params)

    def _update(self, plugin_id, whitelist=None, blacklist=None):
        config_params = dict()
        if whitelist is not None:
            config_params['whitelist'] = whitelist
        if blacklist is not None:
            config_params['blacklist'] = blacklist
        return super(AclPluginInf, self).update(
            plugin_id=plugin_id,
            api_name_or_id=self._api_id,
            plugin_name=self._plugin_name,
            **config_params)

    def _retrieve(self, plugin_id):
        return super(AclPluginInf, self).retrieve(plugin_id)

    def list(self):
        return super(AclPluginInf, self).list(plugin_name=self._plugin_name, api_id=self._api_id)

    def set_acllist(self, whitelist=None, blacklist=None):
        """
        :params: add_whitelist, add_blacklist: list
        """
        num, acl_plugins = self.list()
        acllist = dict()
        if whitelist is not None:
            acllist['whitelist'] = whitelist
        if blacklist is not None:
            acllist['blacklist'] = blacklist
        if not num:
            return self._add(**acllist)
        else:
            acl_plugin_id = acl_plugins[0]['id']
            return self._update(acl_plugin_id, **acllist)

    def get_acllist(self):
        num, acl_plugins = self.list()
        if not num:
            return dict(whitelist=[], blacklist=[])
        else:
            try:
                whitelist = acl_plugins[0]['config']['whitelist']
            except KeyError:
                whitelist = []
            try:
                blacklist = acl_plugins[0]['config']['blacklist']
            except KeyError:
                blacklist = []
            return dict(whitelist=whitelist, blacklist=blacklist)


class GroupInf(object):
    """"""
    def __init__(self, client=client):
        super(GroupInf, self).__init__()
        self._client = client

    def add_consumers2groups(self, username, groups, username_create=True):
        for username in username:
            try:
                exist_groups = self.list(username)
            except ResourceNotFoundError as e:
                if not username_create:
                    raise ResourceNotFoundError(e)
                else:
                    consumer_inf = ConsumerInf()
                    consumer_inf.add(username)
                    exist_groups = []
            for group in groups:
                if group not in exist_groups:
                    req_params = dict(group=group)
                    self._client.execute('POST', 'consumers/%s/acls' % username, req_params)
        return True

    def del_consumers2groups(self, username_or_ids, groups):
        for username_or_id in username_or_ids:
            for group in groups:
                self._del(username_or_id, group)

    def retrieve(self, username_or_id, group):
        req_params = dict(group=group)
        body = self._client.execute('GET', 'consumers/%s/acls' % username_or_id, req_params)
        if len(body['data']):
            return body['data'][0]
        return None

    def list(self, username_or_id):
        body = self._client.execute('GET', 'consumers/%s/acls' % username_or_id)
        groups = list()
        groups_info = body['data']
        for group in groups_info:
            groups.append(group['group'])
        return groups

    def _del(self, username_or_id, group):
        group_info = self.retrieve(username_or_id, group)
        if group_info is None:
            return True
        return self._client.execute(
            'DELETE', 'consumers/%s/acls/%s' % (username_or_id, group_info['id']))


class JwtPluginInf(PluginInf):
    """docstring for JwtInf"""
    def __init__(self, api_id, client=client):
        super(JwtPluginInf, self).__init__(client)
        self._plugin_name = 'jwt'
        self._api_id = api_id

    def add(self, claims_to_verify=['exp', 'nbf'], run_on_preflight=False):
        config_params['claims_to_verify'] = claims_to_verify
        config_params['run_on_preflight'] = run_on_preflight
        return super(JwtPluginInf, self).add(
            plugin_name=self._plugin_name, api_id=self._api_id, **config_params)

    def update(self, plugin_id, claims_to_verify=None, run_on_preflight=None):
        config_params = dict()
        if claims_to_verify is not None:
            config_params['claims_to_verify'] = claims_to_verify
        if run_on_preflight is not None:
            config_params['run_on_preflight'] = run_on_preflight
        return super(AclPluginInf, self).update(
            plugin_id=plugin_id,
            api_name_or_id=self._api_id,
            plugin_name=self._plugin_name,
            api_id=self._api_id,
            **config_params)

    def retrieve(self, plugin_id):
        return super(JwtPluginInf, self).retrieve(plugin_id)

    def list(self):
        return super(JwtPluginInf, self).list(plugin_name=self._plugin_name, api_id=self._api_id)

    def delete(self, plugin_id):
        return super(JwtPluginInf, self).delete(plugin_id=plugin_id, api_name_or_id=self._api_id)


class JwtCredInf(object):
    """docstring for TokenInf"""
    def __init__(self, username_or_id, allow_duplicated=False, client=client):
        """
        :params: allow_duplicated: True or False
                    if not allow duplicated, it willnot create new cred when one or more creds
                    exist.
        """
        super(JwtCredInf, self).__init__()
        self._client = client
        self.username_or_id = username_or_id
        self.allow_duplicated = allow_duplicated

    def add(self):
        """
        :return: credential infomation
        """
        if self.allow_duplicated:
            return self._add_new()
        else:
            self._del_duplicated_jwt_cred()
            num, jwt_creds = self.list()
            if num:
                return self.retrieve(jwt_creds[0]['id'])
            else:
                return self._add_new()

    def _add_new(self):
        return self._client.execute('POST', 'consumers/%s/jwt' % self.username_or_id,
                                    content_type='application/x-www-form-urlencoded')

    def _del_duplicated_jwt_cred(self):
        """
        delete duplicate jwt credentials
        """
        num, jwt_creds = self.list()
        duplicated = 0
        if len(jwt_creds) and isinstance(jwt_creds, list):
            for jwt_cred in jwt_creds:
                duplicated += 1
                if duplicated > 0:
                    self.delete(jwt_cred['id'])
                    logger.info('delete duplicated jwt_cred_id: %s' % jwt_cred['id'])

    def list(self):
        """
        :return: total_num
                 jwt credentials' informations
        """
        body = self._client.execute('GET', 'consumers/%s/jwt' % self.username_or_id)
        return body['total'], body['data']

    def retrieve(self, cred_id):
        return self._client.execute('GET', 'consumers/%s/jwt/%s' % (self.username_or_id, cred_id))

    def delete(self, cred_id):
        return self._client.execute(
            'DELETE', 'consumers/%s/jwt/%s' % (self.username_or_id, cred_id))

    @staticmethod
    def token_gen(key, secret, token_algorithm=TOKEN_ALGORITHM,
                  exp_duration=TOKEN_EXPDURATION, **claims):
        claims['iss'] = key
        claims['nbf'] = datetime.datetime.utcnow()
        claims['exp'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=exp_duration)
        return jwt.encode(claims, secret, algorithm=token_algorithm)

    @staticmethod
    def token_decode(token, secret=None, token_algorithm=TOKEN_ALGORITHM):
        if secret is None:
            return jwt.decode(token, verify=False, algorithm=token_algorithm)
        else:
            try:
                return jwt.decode(token, secret, algorithm=token_algorithm)
            except InvalidSignatureError:
                return None
