# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: daisheng
# Email: shawntai.ds@gmail.com
#

import uuid
from . import app
from flask import request, make_response, json
import datetime
import re
import urllib3
import md5


def gen_uuid(seq=None):
    """
        generate a 32Byte uuid code
    """
    if seq is not None:
        return uuid.uuid1().hex + uuid.uuid3(uuid.NAMESPACE_DNS, seq).hex
    return uuid.uuid1().hex + uuid.uuid3(
        uuid.NAMESPACE_DNS, uuid.uuid1().hex).hex


def hash_pass(password):
    """
        Create a quick list of password.  The password is stored
        as a md5 hash that has also been salted.  You should never
        store the users password and only store the password after
        it has been hashed.
    """
    secreted_password = password + app.config['SECRET_KEY']
    salted_password = md5.new(secreted_password).hexdigest() +\
        app.config['PSW_SALT']
    return md5.new(salted_password).hexdigest()


"""
    logger
"""
# Init the Logging Handler
import logging
from logging import Formatter
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler(app.config['LOGGER_FILE'],
                              maxBytes=102400,
                              backupCount=1)
handler.setFormatter(Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))
handler.setLevel(app.config['DEFAULT_LOGLEVEL'])


def logmsg(msg):
    return '%s' % msg


def logmsg_req(msg, url, method, status_code, resp_data):
    return logmsg('%s(%s[%s]%d:%s)' % (msg, url, method, status_code, resp_data))


"""
    exceptions
"""


class ClientError(Exception):
    """
        invalid API usage, belongs to client exception,
        use the 4xx status_code
    """
    status_code = 400
    message = 'The request cannot be fulfilled due to bad syntax.'

    def __init__(self, message=None, status_code=None, payload=None):
        # setLevel can be [debug, info, warning, error, critical]
        Exception.__init__(self)
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class ServerError(Exception):
    """
        invalid module calling, belongs to server exception,
        use the 5xx status_code
    """
    status_code = 500
    message = 'The server encountered an unexpected condition which \
              prevented it from fulfilling the request.'

    def __init__(self, message=None, status_code=None, payload=None):
        # setLevel can be [debug, info, warning, error, critical]
        Exception.__init__(self)
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


"""
    establish the handler for the custom exceptions
    include formatting errormessage into json type
"""
from flask import jsonify
from . import app


# handler for the InvalidModuleUsage custom exception class
@app.errorhandler(ClientError)
def handle_invalid_module_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


# handler for the InvalidAPIUsage custom exception class
@app.errorhandler(ServerError)
def handle_invalid_api_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


class BadRequestError(ClientError):
    status_code = 400
    message = 'Bad request.'


class AuthenticationError(ClientError):
    status_code = 401
    message = 'Client unauthorized.'


class ResourceNotFoundError(ClientError):
    status_code = 404
    message = "Not Found"


class MethodNotAllowedError(ClientError):
    status_code = 405
    message = 'method not allowed'


class ConflictError(ClientError):
    status_code = 409
    message = 'resource conflicted'


class InternalServerError(ServerError):
    status_code = 500
    message = 'internal server error'


class ServiceUnavailableError(ClientError):
    status_code = 503
    message = "Service Unavailable"


"""
    random options object
"""


class Options(object):
    '''
        Common Options Class
    '''
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    def __getattr__(self, option):
        return None


def to_dict(inst, cls=None, except_clm_list=None, target_clm_list=None, ext_dict=None):
    if isinstance(inst, list):
        print inst
        if not len(inst):
            return inst
        if cls is None:
            cls = inst[0].__class__
        inst_list = inst
        instdict_list = list()
        for inst in inst_list:
            instdict_list.append(
                _to_dict(
                    inst=inst,
                    cls=cls,
                    except_clm_list=except_clm_list,
                    target_clm_list=target_clm_list,
                    ext_dict=ext_dict))
        return instdict_list
    else:
        if cls is None:
            cls = inst.__class__
        return _to_dict(
            inst, cls, except_clm_list=except_clm_list, target_clm_list=target_clm_list,
            ext_dict=ext_dict)


def _to_dict(inst, cls, except_clm_list=None, target_clm_list=None, ext_dict=None):
    """
    Jsonify the sqlalchemy query result.
    """
    convert = dict()
    convert['DATETIME'] = datetime.datetime.isoformat
    # add your coversions for things like datetime's
    # and what-not that aren't serializable.
    d = dict()
    if except_clm_list is None:
        except_clm_list = []
    if target_clm_list is None:
        target_clm_list = []

    for c in cls.__mapper__.columns:
        if len(target_clm_list) and c.name not in target_clm_list:
            continue
        if c.name not in except_clm_list:
            v = getattr(inst, c.name)
            if c.type in convert.keys() and v is not None:
                try:
                    d[c.name] = convert[c.type](v)
                except:
                    d[c.name] = "Error:  Failed to covert using ", \
                        str(convert[c.type])
            elif v is None:
                d[c.name] = str()
            else:
                d[c.name] = v
    if ext_dict is not None:
        d = dict(d, **ext_dict)
    return d


def ip_format_chk(ip_str):
    pattern_string = r"""
       \b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.
       (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.
       (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.
       (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b
       """
    pattern = re.compile(pattern_string, re.X)
    if re.match(pattern, ip_str):
        return True
    else:
        return False


def chk_os_user(os_user):
    if os_user not in app.config['BECOME_USERS']:
        msg = 'invalid become_user(' + os_user + '). Should be ' + \
            '/'.join(app.config['BECOME_USERS']) + '.'
        return [False, msg]
    return [True, 'os_user ' + os_user + ' is good.']


def serial_current_time():
    return datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')


def sort_dict(target_dict, target_key, reverse=False):
    return sorted(target_dict, key=lambda k: k[target_key], reverse=reverse)


def to_unicode(unicode_or_str):
    if isinstance(unicode_or_str, str):
        value = unicode_or_str.decode('utf-8')
    else:
        value = unicode_or_str
    return value


def to_str(unicode_or_str):
    if isinstance(unicode_or_str, unicode):
        value = unicode_or_str.encode('utf-8')
    else:
        value = unicode_or_str
    return value


def try_load_json(json_str):
    try:
        return json.loads(json_str)
    except:
        return json_str


def get_content_type(filename):
    return urllib3.fields.guess_content_type(filename)


def make_json_response(json_str, status_code):
    response = make_response(json_str)
    response.headers["content-type"] = 'application/json'
    response.status_code = status_code
    return response
