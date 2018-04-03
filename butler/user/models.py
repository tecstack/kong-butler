# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#

from .. import db, app
import utils
from ..kong.baseinf import ApiInf, GroupInf, ConsumerInf, JwtPluginInf, AclPluginInf
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

group_inf = GroupInf()
consumer_inf = ConsumerInf()
api_inf = ApiInf()


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
    roles = db.relationship(
        'Role',
        secondary=roles,
        backref=db.backref('roles', lazy='select'))

    def __init__(
            self, username, hashed_password, roles=None, enabled=True, tel=None, email=None):
        self.user_id = utils.gen_uuid(username)
        self.username = username
        self.hashed_password = hashed_password
        self.enabled = enabled
        if tel:
            self.tel = tel
        if email:
            self.email = email
        self.sign_up_date = datetime.datetime.now()

        consumer_inf.add(username)
        if roles is not None:
            self.roles = roles
            for i in range(len(roles)):
                roles[i] = roles[i].role_name
            group_inf.add_consumers2groups([username], roles)

    def __repr__(self):
        return '<User %r>' % self.user_id

    def save(self):
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
        # ext_dict['privilege'] = utils.to_dict(inst=self.get_privs(), except_clm_list=['deleted'])
        ext_dict['role'] = utils.to_dict(inst=self.get_roles(), except_clm_list=['enabled'])
        user_dict = utils.to_dict(inst=self, except_clm_list=['hashed_password'], ext_dict=ext_dict)
        return user_dict

#    def get_short_dict_info(self):
#        ext_dict = dict()
#        ext_dict['role'] = utils.to_dict(
#            inst=self.get_roles(), target_clm_list=['role_id', 'role_name', 'description'])
#        user_dict = utils.to_dict(
#            inst=self, except_clm_list=['hashed_password', 'sign_up_date', 'last_login'],
#            ext_dict=ext_dict)
#        return user_dict

    def get_roles(self, only_enabled=True):
        roles = self.roles
        tar_roles = list()
        if only_enabled:
            return roles
        for role in roles:
            if role.enabled:
                tar_roles.append(role)
        return tar_roles

    def update(self, username=None, hashed_password=None, last_login=None, tel=None, email=None,
               enabled=None, role_list=None):
        if username is not None:
            self.username = username
        if hashed_password is not None:
            self.hashed_password = hashed_password
        if last_login is not None:
            self.last_login = last_login
        if tel is not None:
            self.tel = tel
        if email is not None:
            self.email = email
        if enabled is not None:
            self.enabled = enabled
        if role_list is not None:
            self.roles = role_list
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

    def __init__(self, role_name, description=None, users=None, privileges=None, enabled=True):
        self.role_id = utils.gen_uuid(role_name)
        self.role_name = role_name
        self.description = description
        self.enabled = enabled
        if users is not None:
            self.users = users

    def save(self):
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

    def update(self, role_name=None, users=None, description=None, enabled=None):
        if role_name is not None:
            pass
        if users is not None:
            self.users = users
        if description is not None:
            self.description = description
        if enabled is not None:
            self.enabled = enabled
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
        tar_users = list()
        for user in users:
            if user.enabled:
                tar_users.append(user)
        return tar_users

    def get_dict_info(self):
        ext_dict = dict()
        ext_dict['user'] = utils.to_dict(inst=self.get_users(), except_clm_list=['enabled'])
        role_dict = utils.to_dict(inst=self, ext_dict=ext_dict)
        return role_dict

    def asso_kong_apis(self, api_ids):
        for api_id in api_ids:
            acl_inf = AclPluginInf(api_id)
            acl_inf.set_acllist(whitelist=[self.role_name])

    def asso_kong_consumers(self, users):
        usernames = list()
        for user in users:
            usernames.append(user.username)
        return group_inf.add_consumers2groups(usernames, [self.role_name])

    def delete(self):
        self.users = []
        self.save()
        db.session.delete(self)
        db.session.commit()


class Api(object):
    """docstring for Api"""
    def __init__(self, api_id):
        super(Api, self).__init__()
        self.api_id = api_id

    @staticmethod
    def get_list():
        num, data = api_inf.list()
        return data

    @classmethod
    def get_api_ids(cls):
        apis = cls.get_list()
        for i in range(len(apis)):
            apis[i] = apis[i]['id']
        return apis

    def api_info(self):
        return api_inf.retrieve(api_id=self.api_id)

    def add_roles(self, api_id, roles):
        for i in range(len(roles)):
            roles[i] = roles[i]['role_name']
        acl_inf = AclPluginInf(api_id=self.api_id)
        acl_inf.set_acllist(whitelist=roles)


def init_user_data():
    # init user data: create all privileges and super user

    try:
        role_root = Role.get_roles(role_name='root')[0]
    except IndexError:
        role_root = Role(role_name='root', description='超级用户')
        role_root.save()
    role_root.asso_kong_apis(Api.get_api_ids())

    try:
        user_root = User.get_users(username=app.config['DEFAULT_ROOT_USERNAME'])[0]
    except IndexError:
        user_root = User(
            username=app.config['DEFAULT_ROOT_USERNAME'],
            hashed_password=utils.hash_pass(app.config['DEFAULT_ROOT_PASSWORD']))
        user_root.save()

    if not role_root.asso_kong_consumers([user_root]):
        user_root.update(role_list=[role_root])
        print 'asso kong consumer to roles error.'

    print 'User Data imported'
