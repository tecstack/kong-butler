# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#

from .. import db, app
import utils
from ..kong.kongadm import Consumer, Group, KongApi
from ..kong.client import Client as KongClient
from ..kong.exceptions import KongError
# from sqlalchemy import sql, and_

import datetime

logger = app.logger

"""
This is a HELPER table for the role_table and user_table to set up
the many-to-many relationship between Role modole and User model.
As Flask official documentation recommanded, this helper table
should not be a model but an actual table.
"""
roles = db.Table(
    'roles',
    db.Column(
        'role_id',
        db.String(64),
        db.ForeignKey('role.role_id')),
    db.Column(
        'user_id',
        db.String(64),
        db.ForeignKey('user.user_id'))
)


class User(db.Model):
    """
    User model
    """
    __tablename__ = 'user'
    # user_id is a 64Byte UUID depend on the timestamp, namespace and username
    user_id = db.Column(db.String(64), primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    hashed_password = db.Column(db.String(128))
    enabled = db.Column(db.Boolean)
    last_login = db.Column(db.DATETIME)
    tel = db.Column(db.String(32))
    email = db.Column(db.String(32))
    sign_up_date = db.Column(db.DATETIME)
    consumer_id = db.Column(db.String(64))
    roles = db.relationship(
        'Role',
        secondary=roles,
        backref=db.backref('roles', lazy='select'))

    def __init__(
            self, username, password, roles=None, enabled=True, tel=None, email=None):
        self.user_id = utils.gen_uuid(username)
        self.username = username
        self.hashed_password = utils.hash_pass(password)
        self.enabled = enabled
        if tel:
            self.tel = tel
        if email:
            self.email = email
        self.sign_up_date = datetime.datetime.now()
        self.consumer_id = Consumer(self.username).consumer_id
        self.save()

    def __repr__(self):
        return '<User %r>' % self.user_id

    def save(self):
        [state_kong, msg_kong] = self._save_to_kong()
        [state_db, msg_db] = self._save_to_db()
        return [state_kong and state_db, msg_kong + msg_db]

    def _save_to_db(self):
        self._save_to_kong()
        db.session.add(self)
        try:
            db.session.commit()
            msg = utils.logmsg('user saved<%s:%s>.' % (self.username, self.user_id))
            state = True
        except Exception, e:
            db.session.rollback()
            msg = utils.logmsg('exception: %s.' % e)
            app.logger.info(msg)
            state = False
        return [state, msg]

    def _save_to_kong(self):
        try:
            con = Consumer.get(self.consumer_id)
            con.username = self.username
            con.groups = [role.role_name for role in self.roles]
            msg = utils.logmsg(
                'user name/groups save to kong.<%s:%s>' % (self.username, self.user_id))
            state = True
        except KongError as e:
            msg = utils.logmsg('KongError: %s' % e)
            app.logger.error(msg)
            state = False
        return [state, msg]

    @staticmethod
    def get_users(username=None, user_id=None, only_enabled=True):
        args = dict()
        if only_enabled:
            args['enabled'] = True
        if username is not None:
            args['username'] = username
        if user_id is not None:
            args['user_id'] = user_id
        users = User.query.filter_by(**args).all()
        return users

    def get_dict_info(self):
        ext_dict = dict()
        ext_dict['role'] = utils.to_dict(inst=self.get_roles(), except_clm_list=['enabled'])
        user_dict = utils.to_dict(
            inst=self, except_clm_list=['hashed_password', 'consumer_id'], ext_dict=ext_dict)
        return user_dict

    def get_roles(self, only_enabled=True):
        roles = self.roles
        if only_enabled:
            return roles
        tar_roles = list()
        for role in roles:
            if role.enabled:
                tar_roles.append(role)
        return tar_roles

    def update(self, username=None, password=None, last_login=None, tel=None, email=None,
               enabled=None, roles=None):
        if username is not None:
            Consumer.get(self.consumer_id).username = username
            self.username = username
        if password is not None:
            self.hashed_password = utils.hash_pass(password)
        if last_login is not None:
            self.last_login = last_login
        if tel is not None:
            self.tel = tel
        if email is not None:
            self.email = email
        if enabled is not None:
            self.enabled = enabled
        if roles is not None:
            Consumer.get(self.consumer_id).groups = [role.role_name for role in roles]
            self.roles = roles
        app.logger.debug(utils.logmsg('user info update<%s:%s>' % (self.username, self.user_id)))
        [state, msg] = self.save()
        if not state:
            app.logger.error(utils.logmsg(msg))
            return [False, 'user update faild.']
        return [state, 'user updated.']

    def delete(self):
        self.roles = []
        self.save()
        db.session.delete(self)
        db.session.commit()


class Role(db.Model):
    """
    role model
    """
    __tablename__ = 'role'
    # role_id is a 64Byte UUID depend on the timestamp, namespace and rolename
    role_id = db.Column(db.String(64), primary_key=True)
    role_name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    enabled = db.Column(db.Boolean)
    users = db.relationship(
        'User',
        secondary=roles,
        backref=db.backref('role', lazy='select'))

    def __repr__(self):
        return '<Role %r>' % self.role_id

    def __init__(self, role_name, description=None, users=None, enabled=True, api_ids=None):
        self.role_id = utils.gen_uuid(role_name)
        self.role_name = role_name
        self.description = description
        self.enabled = enabled
        if users is not None:
            self.users = users
        if api_ids is not None:
            self.api_ids = api_ids

    def save(self):
        [state_kong, msg_kong] = self._save_to_kong()
        [state_db, msg_db] = self._save_to_db()
        return [state_kong and state_db, msg_kong + msg_db]

    def _save_to_kong(self):
        try:
            group = Group(self.role_name)
            users = self.users
            group.usernames = [user.username for user in users]
            msg = utils.logmsg(
                'role usernames save to kong.<%s:%s>' % (self.role_name, self.role_id))
            state = True
        except KongError as e:
            msg = utils.logmsg('KongError: %s' % e)
            app.logger.error(msg)
            state = False
        return [state, msg]

    def _save_to_db(self):
        db.session.add(self)
        try:
            db.session.commit()
            msg = utils.logmsg('role saved<%s:%s>.' % (self.role_name, self.role_id))
            app.logger.debug(msg)
            state = True
        except Exception, e:
            db.session.rollback()
            msg = utils.logmsg(
                'exception saving role<%s:%s>: %s.' % (self.role_name, self.role_id, e))
            app.logger.info(msg)
            state = False
        return [state, msg]

    def update(self, role_name=None, users=None, description=None, api_ids=None, enabled=None):
        if users is not None:
            self.users = users
        if description is not None:
            self.description = description
        if enabled is not None:
            if self.enabled is False and enabled is True:
                group = Group(self.role_name)
                group.usernames = [user.username for user in self.users]
                group.api_ids = self.api_ids
            elif self.enabled is True and enabled is False:
                group.delete()
            self.enabled = enabled
        if api_ids is not None:
            group = Group(self.role_name)
            group.api_ids = api_ids
        if role_name is not None:
            if self.get_roles(role_name=role_name):
                msg = 'role_name in used.<%s>' % role_name
                app.logger.info(utils.logmsg(msg))
                return [False, msg]
            else:
                Group(self.role_name).delete()
                group = Group(role_name)
                group.api_ids = self.api_ids
                users = self.users
                group.usernames = [user.username for user in users]
                self.role_name = role_name
        app.logger.debug(utils.logmsg('role info update<%s:%s>.' % (self.role_name, self.role_id)))
        [state, msg] = self.save()
        if not state:
            app.logger.info(utils.logmsg(msg))
            return [False, 'role update faild.']
        return [True, 'role updated.']

    @staticmethod
    def get_roles(role_name=None, role_id=None, only_enabled=True):
        args = dict()
        if only_enabled:
            args['enabled'] = True
        if role_name is not None:
            args['role_name'] = role_name
        if role_id is not None:
            args['role_id'] = role_id
        roles = Role.query.filter_by(**args).all()
        return roles

    def get_users(self, only_enabled=True):
        users = self.users
        if not only_enabled:
            return users
        return [user for user in users if user.enabled]

    @property
    def api_ids(self):
        return Group(self.role_name).api_ids

    @api_ids.setter
    def api_ids(self, tar_api_ids):
        if isinstance(tar_api_ids, list):
            Group(self.role_name).api_ids = tar_api_ids

    def get_dict_info(self):
        ext_dict = dict()
        ext_dict['api'] = Api.list()
        ext_dict['user'] = utils.to_dict(inst=self.get_users(), except_clm_list=['enabled'])
        role_dict = utils.to_dict(inst=self, ext_dict=ext_dict)
        return role_dict

    def delete(self):
        self.users = []
        self.save()
        db.session.delete(self)
        db.session.commit()


class Api(object):
    """docstring for Api"""
    def __new__(cls, api_id):
        kongapi = KongApi(api_id)
        if kongapi is None:
            return None
        api = super(Api, cls).__new__(cls)
        api.kongapi = KongApi
        api.api_id = api_id
        return api

    def __init__(self, api_id):
        super(Api, self).__init__()

    @staticmethod
    def list():
        return KongApi.list()

    @classmethod
    def list_api_ids(cls):
        apis = cls.list()
        return [api['id'] for api in apis]

    def get(api_id):
        pass

    @staticmethod
    def _chk_kong(api_id):
        pass

    @property
    def info(self):
        return self.kongapi.info

    @property
    def role_names(self):
        return self.kongapi.whitelist

    @role_names.setter
    def role_names(self, tar_role_names):
        if isinstance(tar_role_names, list):
            self.kongapi.whitelist = tar_role_names


def init_user_data():
    # init user data: create all privileges and super user

    try:
        role_root = Role.get_roles(role_name=app.config['DEFAULT_ROOT_ROLENAME'])[0]
    except IndexError:
        role_root = Role(role_name=app.config['DEFAULT_ROOT_ROLENAME'], description='超级用户')
        role_root.save()
    role_root.update(api_ids=Api.list_api_ids())

    try:
        user_root = User.get_users(username=app.config['DEFAULT_ROOT_USERNAME'])[0]
    except IndexError:
        user_root = User(
            username=app.config['DEFAULT_ROOT_USERNAME'],
            password=app.config['DEFAULT_ROOT_PASSWORD'])
        user_root.save()

    user_root.update(roles=[role_root])

    print 'User Data imported'
