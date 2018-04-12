# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is the auth module of user package,
# using to user authutification including
# authentication(login by user&password, login by token),
# autherization(privilege auth by token, etc.)
#

from flask import g, request
from flask_restful import reqparse, Resource
from ..user.models import User
from ..kong.kongadm import JwtCred
from ..kong.baseinf import JwtCredInf
from .. import app
from . import utils
import datetime
import time


class LoginAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(LoginAPI, self).__init__()

    def post(self):
        username, password = self._post_arg_check()

        [user, last_login] = login(username, password)
        msg = 'user logged in.<user:%s>' % user.username
        response = {"message": msg,
                    "token": get_token(user),
                    "user_info": user.get_dict_info()}
        return response, 200

    def _post_arg_check(self):
        self.reqparse.add_argument(
            'username', type=str, location='json',
            required=True, help='user name must be string')
        self.reqparse.add_argument(
            'password', type=str, location='json',
            required=True, help='password must be string')
        args = self.reqparse.parse_args()
        username = args['username']
        password = args['password']
        return username, password


class TokenAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(TokenAPI, self).__init__()

    def post(self):
        token = self._post_arg_check()

        user_id = JwtCred.get_user_id(token)
        try:
            user = User.get_users(user_id=user_id)[0]
        except:
            raise utils.AuthenticationError('wrong user_id in token.')
            app.logger.info(utils.logmsg('wrong user_id in token.'))
        msg = 'user reflesh token.<user:%s>' % user.username
        response = {"message": msg,
                    "token": get_token(user),
                    "user_info": user.get_dict_info()}
        return response, 200

    def _post_arg_check(self):
        self.reqparse.add_argument(
            'token', type=str, location='headers',
            required=True, help='token must be string')
        args = self.reqparse.parse_args()
        return args['token']


def login(username, password):
    users = User.get_users(username=username)
    if not users:
        msg = 'Cannot find user<username:' + username + '>.'
        app.logger.debug(utils.logmsg(msg))
        raise utils.AuthenticationError(msg)
    user = users[0]
    if not utils.hash_pass(password) == user.hashed_password:
        msg = 'user name and password cannot match.'
        app.logger.debug(utils.logmsg(msg))
        raise utils.AuthenticationError(msg)
    last_login = user.last_login
    user.last_login = datetime.datetime.utcnow()
    user.save()
    return [user, last_login]


def get_token(user):
    return JwtCred(user).token
