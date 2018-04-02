# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com

from flask_restful import reqparse, Resource
from .models import User, Role, Api
from .. import app
import utils


class UserAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(UserAPI, self).__init__()

    def get(self):
        """
        get user list or one user info
        """
        user = self._get_arg_check()
        if user is None:
            msg = 'user infomation.<user:%s>' % user.username
            user_info = user.get_dict_info()
            return {"message": msg, "user_info": user_info}, 200
        else:
            users = User.get_users()
            user_info_list = list()
            for user in users:
                user_info = user.get_dict_info()
                user_info_list.append(user_info)
            msg = "infomations of all users."
            return {'message': msg, 'user_list': user_info_list}, 200

    def _get_arg_check(self):
        self.reqparse.add_argument(
            'user_id', type=str, location='args', help='user_id must be string.')

        args = self.reqparse.parse_args()
        user_id = args['user_id']
        if user_id:
            users = User.get_users(user_id=user_id)
            if users:
                return users[0]
            else:
                msg = 'invalid user_id<%s>' % user_id
                app.logger.debug(utils.logmsg(msg))
                raise utils.ResourceNotFoundError(msg)
        return None

    def post(self):
        """
        add a new user
        """
        [username, password, role_list, tel, email] = self._post_arg_check()

        # add the new user
        user = User(
            username=username,
            hashed_password=utils.hash_pass(password),
            roles=role_list,
            tel=tel,
            email=email)
        user.save()
        msg = 'user created.<user:' + user.user_id + '>'
        app.logger.info(msg)
        response = {"message": msg, "user_id": user.user_id}
        return response, 200

    def _post_arg_check(self):
        self.reqparse.add_argument(
            'username', type=str, location='json',
            required=True, help='user name must be string')
        self.reqparse.add_argument(
            'password', type=str, location='json',
            required=True, help='password must be string')
        self.reqparse.add_argument(
            'role_id_list', type=list, location='json',
            help='role id must be string list')
        self.reqparse.add_argument(
            'tel', type=str, location='json',
            help='tel must be str')
        self.reqparse.add_argument(
            'email', type=str, location='json',
            help='email must be str')

        args = self.reqparse.parse_args()
        username = args['username']
        password = args['password']
        tel = args['tel']
        email = args['email']

        role_id_list = args['role_id_list']
        if role_id_list:
            role_list = list()
            for role_id in role_id_list:
                roles = Role.get_roles(role_id=role_id)
                if not roles:
                    msg = 'invalid role id:%s' % role_id
                    app.logger.debug(utils.logmsg(msg))
                    raise utils.ResourceNotFoundError(msg)
                role_list.append(roles[0])
        else:
            role_list = None

        users = User.get_users(username=username)
        if users:
            msg = 'user name<%s> in used.' % username
            app.logger.debug(utils.logmsg(msg))
            raise utils.ResourceNotFoundError(msg)

        return [username, password, role_list, tel, email]

#    def delete(self):
#        """
#        delete a user
#        """
#        user = self._delete_arg_check()#

#        # delete the new user
#        [state, msg] = user.delete()
#        if not state:
#            msg = 'delete user faild.'
#            app.logger.info(utils.logmsg(msg))
#            raise utils.ServerError(msg)#

#        msg = 'user deleted.'
#        app.logger.info(msg + '<user_id:%s>' % user.user_id)
#        response = {"message": msg, "user_id": user.user_id}
#        return response, 200#

#    def _delete_arg_check(self):
#        self.reqparse.add_argument(
#            'user_id', type=str, location='args',
#            required=True, help='user_id must be string.')#

#        args = self.reqparse.parse_args()
#        user_id = args['user_id']
#        users = User.get_users(user_id=user_id)
#        if not users:
#            msg = 'invalid user_id<%s>' % user_id
#            app.logger.debug(utils.logmsg(msg))
#            raise utils.ResourceNotFoundError(msg)
#        return users[0]

    def put(self):
        """
        modf a user
        """
        [target_user, username, hashed_password, role_list, tel, email, enabled] = \
            self._put_arg_check()
        # update user
        target_user.update(
            username=username, hashed_password=hashed_password,
            role_list=role_list, tel=tel, email=email, enabled=enabled)
        target_user.save()
        msg = 'user updated.<user:%s' % target_user.user_id
        app.logger.info(msg)
        response = {"message": msg, "user_id": target_user.user_id}
        return response, 200

    def _put_arg_check(self):
        self.reqparse.add_argument(
            'user_id', type=str, location='args',
            required=True, help='user name must be string')
        self.reqparse.add_argument(
            'username', type=str, location='json',
            help='user name must be string')
        self.reqparse.add_argument(
            'password', type=str, location='json',
            help='password must be string')
        self.reqparse.add_argument(
            'role_id_list', type=list, location='json',
            help='role id must be string list')
        self.reqparse.add_argument(
            'tel', type=str, location='json',
            help='tel must be str')
        self.reqparse.add_argument(
            'email', type=str, location='json',
            help='email must be str')
        self.reqparse.add_argument(
            'enabled', type=bool, location='json',
            help='enabled must be boolean')

        args = self.reqparse.parse_args()
        # required args check
        user_id = args['user_id']
        target_users = User.get_users(user_id=user_id)
        if not target_users:
            msg = 'invalid user_id<%s>' % user_id
            app.logger.debug(utils.logmsg(msg))
            raise utils.ClientUnprocEntError(msg)
        target_user = target_users[0]

        # other args check
        role_id_list = args['role_id_list']
        role_list = list()
        if role_id_list:
            for role_id in role_id_list:
                roles = Role.get_roles(role_id=role_id)
                if not roles:
                    msg = 'invalid role id<%s>' % role_id
                    app.logger.debug(utils.logmsg(msg))
                    raise utils.ResourceNotFoundError(msg)
                role_list.append(roles[0])

        password = args['password']
        if password:
            hashed_password = utils.hash_pass(password)
        else:
            hashed_password = None

        tel = args['tel']
        email = args['email']

        username = args['username']
        if username:
            users = User.get_users(username=username)
            for user in users:
                if not user.user_id == user_id:
                    msg = 'user name<%s> in used.' % username
                    app.logger.debug(utils.logmsg(msg))
                    raise utils.ResourceNotFoundError(msg)
        elif username is '':
            msg = 'user name should not be empty string.'
            app.logger.debug(utils.logmsg(msg))
            raise utils.ResourceNotFoundError(msg)

        enabled = args['enabled']
        return [target_user, username, hashed_password, role_list, tel, email, enabled]
