# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: daisheng
# Email: shawntai.ds@gmail.com

import utils
import json
from exceptions import *

from requests import Session, request
from requests.auth import AuthBase
from requests.auth import HTTPBasicAuth
from requests.exceptions import ReadTimeout

logger = utils.logger


APIKEY_NAME = 'key'


class KeyAuth(AuthBase):
    """Attaches HTTP Key Authentication to the given Request object."""
    def __init__(self, apikey):
        self.apikey = apikey

    def __call__(self, r):
        r.headers[APIKEY_NAME] = self.apikey
        return r


class Client(object):
    """docstring for client"""

    def __init__(self, base_url, apikey=None, basic_auth=None, use_session=False, timeout=10):
        """
        set credential of client to Authorization of kong admin
        :param base_url: kong admin base url
        :param apikey: apikey auth string
        :param basic_auth: dict of 'username', 'password'
        """
        from . import __version__
        self.headers = {
            'User-Agent': 'bulter-kong/' + __version__,
            'AcceptEncoding': 'gzip, deflate',
            'Accept': 'application/json',
        }
        self.base_url = base_url
        self.auth = self._init_auth(apikey=apikey, basic_auth=basic_auth)
        if use_session:
            self._session = Session()
        else:
            self._session = None
        self.timeout = timeout

    def chk_conn(self, status_path='status'):
        try:
            body = self.execute('GET', status_path)
            db_reachable = body['database']['reachable']
        except ReadTimeout as e:
            raise KongAdmConnectionTimeoutError(e)
        except AuthenticationError as e:
            raise KongAdmAuthFaildError(e)
        except ForbiddenError as e:
            raise KongAdmPermissionError(e)
        except Exceptions as e:
            raise KongAdmUnkownConnError(e)
        if not db_reachable:
            raise KongAdmDBUnreachable('kong database unreachable.<url:%s>' % self.base_url)
        return True

    def destroy(self):
        if self._session is not None:
            self._session.close()
        self._session = None

    def _init_auth(self, apikey=None, basic_auth=None):
        """
        set credential of client to Authorization of kong admin
        :param apikey: apikey auth string
        :param basic_auth: ['username'], ['password']
        """
        if apikey is not None:
            return KeyAuth(apikey)
        if basic_auth is not None:
            return HTTPBasicAuth(basic_auth['username'], basic_auth['password'])
        else:
            return None

    def execute(self, http_method, path, params=None, content_type='application/json'):
        """ Construct an API request, send it to the API, and parse the response. """
        url = self.base_url + self.format_path(path)
        req_params = dict()

        if self.auth is not None:
            req_params['auth'] = self.auth

        if http_method in ('POST', 'PUT', 'PATCH'):
            self.headers['content-type'] = content_type
            if params is not None:
                req_params['data'] = json.dumps(params, cls=ResourceEncoder)
        elif http_method in ('GET', 'DELETE'):
            req_params['params'] = params
        else:
            logger.error('request to %s, Wrong http_method: %s' % (url, http_method))
            return None
        req_params['headers'] = self.headers

        # request logging
        logger.debug("Sending %s request to: %s", http_method, url)
        logger.debug("  headers: %s", self.headers)
        if 'params' in req_params:
            logger.debug("  params: %s", req_params['params'])
        if 'data' in req_params:
            logger.debug("  params: %s", req_params['data'])

        if self._session is None:
            resp = request(http_method, url, timeout=self.timeout, **req_params)
        else:
            resp = self._session.request(
                http_method, url, timeout=self.timeout, **req_params)
        # response logging
        logger.debug("Response received from %s", url)
        logger.debug("  encoding=%s status:%s", resp.encoding, resp.status_code)
        logger.debug("  content:\n%s", resp.content)

        return self.parse_body(resp)

    def parse_body(self, resp):
        if resp.status_code in error_codes:
            message = 'kong response: %s, status_code:%d, url:%s, content:%s' % (
                resp.request.method, resp.status_code, resp.url, resp.content)
            raise error_codes[resp.status_code](message)

        if resp.content and resp.content.strip():
            try:
                # use supplied or inferred encoding to decode the
                # response content
                decoded_body = resp.content.decode(resp.encoding or resp.apparent_encoding)
                data = json.loads(decoded_body)
                return data
            except Exception, e:
                logger.error('kong response body parse error: %s, url:%s, content:%s' % (
                    e, resp.url, resp.content))
                return None

    @staticmethod
    def format_path(path=None):
        """set path into '/xx/xx/xx' format."""
        if path is None or path == '/' or len(path) == 0:
            return ''
        if not path[0] == '/':
            path = '/' + path
        if path[-1] == '/':
            path = path[:-1]
        return path


class ResourceEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'attributes'):
            # handle API resources
            return o.attributes
        return super(ResourceEncoder, self).default(o)
