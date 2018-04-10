# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: daisheng
# Email: shawntai.ds@gmail.com
#

from ..utils import *


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
