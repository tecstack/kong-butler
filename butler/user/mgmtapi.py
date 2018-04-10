# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com

from flask_restful import reqparse, Resource
from .models import User, Role, Api
from .. import app
import utils
from ..kong.exceptions import ResourceNotFoundError as KongResourceNotFoundError


class UserAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(UserAPI, self).__init__()

    def get(self):
        """
        get user list or one user info
        """
        user = self._get_arg_check()
        if user is not None:
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
            password=password,
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

    def put(self):
        """
        modf a user
        """
        [target_user, username, password, roles, tel, email, enabled] = \
            self._put_arg_check()
        # update user
        target_user.update(
            username=username, password=password,
            roles=roles, tel=tel, email=email, enabled=enabled)
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
            'role_ids', type=list, location='json',
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
        role_ids = args['role_ids']
        roles = list()
        if role_ids:
            for role_id in role_ids:
                got_roles = Role.get_roles(role_id=role_id)
                if not got_roles:
                    msg = 'invalid role id<%s>' % role_id
                    app.logger.debug(utils.logmsg(msg))
                    raise utils.ResourceNotFoundError(msg)
                roles.append(got_roles[0])

        password = args['password']

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
        return [target_user, username, password, roles, tel, email, enabled]


class RoleAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(RoleAPI, self).__init__()

    def get(self):
        """
        get role list or one role info
        """
        role = self._get_arg_check()
        if role:
            msg = 'role infomation.<role:' + role.role_name + '>'
            return {
                'message': msg,
                'role_info': role.get_dict_info()}, 200
        else:
            roles = Role.get_roles()
            role_info_list = list()
            for role in roles:
                role_info = role.get_dict_info()
                role_info_list.append(role_info)
            msg = "infomations of all roles."
            return {"message": msg, "role_list": role_info_list}, 200

    def _get_arg_check(self):
        self.reqparse.add_argument(
            'role_id', type=str, location='args', help='role_id must be string.')

        args = self.reqparse.parse_args()
        role_id = args['role_id']
        if role_id:
            roles = Role.get_roles(role_id=role_id)
            if not roles:
                msg = 'invalid role_id.'
                app.logger.debug(utils.logmsg(msg))
                raise utils.ResourceNotFoundError(msg)
            return roles[0]
        return None

    def post(self):
        """
        add a new role
        """
        [role_name, description, users, api_ids] = self._post_arg_check()

        role = Role(role_name=role_name, description=description, users=users, api_ids=api_ids)
        role.save()
        msg = 'role created.'
        app.logger.info(msg)
        response = {"message": msg, "role_id": role.role_id}
        return response, 200

    def _post_arg_check(self):
        self.reqparse.add_argument(
            'role_name', type=str, location='json', required=True, help='role name must be string')
        self.reqparse.add_argument(
            'description', type=unicode, location='json', help='description must be string')
        self.reqparse.add_argument(
            'api_ids', type=list, location='json', help='privilege id must be string list')
        self.reqparse.add_argument(
            'user_ids', type=list, location='json', help='user id must be list')

        args = self.reqparse.parse_args()
        role_name = args['role_name']
        description = args['description']
        api_ids = args['api_ids']
        user_ids = args['user_ids']

        roles = Role.get_roles(role_name=role_name)
        if roles:
            msg = 'role name is in used.'
            app.logger.debug(utils.logmsg(msg))
            raise utils.ResourceNotFoundError(msg)
        users = list()
        if user_ids:
            for user_id in user_ids:
                got_users = User.get_users(user_id=user_id)
                if not got_users:
                    msg = 'invalid user id<%s>' % user_id
                    app.logger.debug(utils.logmsg(msg))
                    raise utils.ResourceNotFoundError(msg)
                users.append(got_users[0])

        if api_ids:
            for api_id in api_ids:
                api = Api(api_id)
                if api is None:
                    msg = 'api not found<%s>' % api_id
                    app.logger.debug(utils.msg(msg))
                    raise utils.ResourceNotFoundError(msg)

        return [role_name, description, users, api_ids]

    def put(self):
        """
        modf a role
        """
        [role, role_name, description, users, api_ids, enabled] = self._put_arg_check()

        # update user
        [state, msg] = role.update(role_name=role_name, users=users, description=description,
                                   api_ids=api_ids, enabled=enabled)
        if not state:
            app.logmsg.info(utils.logmsg(msg))
            raise utils.ServerError(msg)

        msg = 'role updated.<%s>' % role.role_id
        app.logger.info(utils.logmsg(msg))
        response = {"message": msg, "role_id": role.role_id}
        return response, 200

    def _put_arg_check(self):
        self.reqparse.add_argument(
            'role_id', type=str, location='args', required=True, help='role_id must be string')
        self.reqparse.add_argument(
            'role_name', type=str, location='json', help='role name must be string')
        self.reqparse.add_argument(
            'description', type=unicode, location='json', help='description must be string')
        self.reqparse.add_argument(
            'user_ids', type=list, location='json', help='user id must be list')
        self.reqparse.add_argument(
            'api_ids', type=list, location='json', help='api ids must be list')
        self.reqparse.add_argument(
            'enabled', type=bool, location='json', help='enabled must be boolean')

        args = self.reqparse.parse_args()
        role_id = args['role_id']
        role_name = args['role_name']
        description = args['description']
        user_ids = args['user_ids']
        api_ids = args['api_ids']
        enabled = args['enabled']

        roles = Role.get_roles(role_id=role_id)
        if not roles:
            msg = 'role not found<%s>' % role_id
            app.logger.debug(msg)
            raise utils.ResourceNotFoundError(msg)
        role = roles[0]

        if role_name is not None:
            roles_by_name = Role.get_roles(role_name=role_name)
            if roles_by_name:
                role_by_name = roles_by_name[0]
                if not role.role_id == role_by_name.role_id:
                    msg = 'role name is in used<%s>' % role_name
                    app.logger.debug(utils.logmsg(msg))
                    raise utils.ConflictError(msg)
        users = list()
        if user_ids:
            for user_id in user_ids:
                got_users = User.get_users(user_id=user_id)
                if not got_users:
                    msg = 'invalid user id<%s>' % user_id
                    app.logger.debug(utils.logmsg(msg))
                    raise utils.ResourceNotFoundError(msg)
                users.append(got_users[0])
        if api_ids:
            for api_id in api_ids:
                api = Api(api_id)
                if api is None:
                    msg = 'api not found<%s>' % api_id
                    app.logger.debug(utils.msg(msg))
                    raise utils.ResourceNotFoundError(msg)
        return [role, role_name, description, users, api_ids, enabled]


class ApiAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(ApiAPI, self).__init__()

    def get(self):
        """
        get role list or one role info
        """
        api = self._get_arg_check()
        if api:
            msg = 'api infomation.<api:%s>' % api.api_id
            return {
                'message': msg,
                'api_info': api.info}, 200
        else:
            msg = "infomations of all roles."
            return {"message": msg, "api_list": Api.list()}, 200

    def _get_arg_check(self):
        self.reqparse.add_argument(
            'api_id', type=str, location='args', help='api_id must be string.')

        args = self.reqparse.parse_args()
        api_id = args['api_id']
        if api_id:
            api = Api(api_id)
            return api
        return None
