# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: daisheng
# Email: shawntai.ds@gmail.com

import utils
from client import Client
from exceptions import *


logger = utils.logger


class NodeInf(object):
    """docstring for KongNode"""
    def __init__(self, client):
        super(NodeInf, self).__init__()
        self._client = client

    def retrieve_info(self):
        return self._client.execute('GET', '', None)

    def retrieve_status(self):
        return self._client.execute('GET', 'status', None)


class ConsumerInf(object):
    """docstring for Consumer"""
    def __init__(self, client):
        super(ConsumerInf, self).__init__()
        self._client = client

    def add(self, username):
        """
        :return: id of consumer
        """
        consumer_id = self.retrieve(username)
        if consumer_id is not None:
            raise UsernameDuplicateError('username<%s> duplicated.' % username)

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
            return self._client.execute('GET', 'consumers/%s' % username_or_id, None)
        except ResourceNotFoundError:
            return None

    def list(self):
        """
        :return: total_num, consumers list
        """
        body = self._client.execute('GET', 'consumers', None)
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
            return self._client.execute('DELETE', 'consumers/%s' % username_or_id, None)
        except ResourceNotFoundError:
            logger.info('username_or_id<%s> not found when deleting consumer.' % username_or_id)
            return None


class ApiInf(object):
    """docstring for api"""
    def __init__(self, client):
        super(ApiInf, self).__init__()
        self._client = client

    def add(self):
        pass

    def retrieve(self, name_or_id):
        """
        :return: api info
        """
        try:
            return self._client.execute('GET', 'apis/%s' % name_or_id, None)
        except ResourceNotFoundError:
            return None

    def list(self):
        """
        :return: total_num, api list
        """
        body = self._client.execute('GET', 'apis', None)
        return body['total'], body['data']


class PluginInf(object):
    """docstring for Plugin"""
    def __init__(self, client):
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
        return self._client.execute('GET', 'plugins/%s' % plugin_id, None)

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
            req_params['api_id'] = plugin_name
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
        body = self._client.execute('GET', 'apis/%s/plugins' % api_id, None)
        return body['total'], body['data']

    def delete(self, plugin_id, api_name_or_id):
        """

        :return:
        """
        return self._client.execute(
            'DELETE', 'apis/%s/plugins/%s' % (api_name_or_id, plugin_id), None)

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
