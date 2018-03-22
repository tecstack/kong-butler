# -*- coding:utf-8 -*-
# !/usr/bin/env python

from nose.tools import *

class Options(object):
    '''
        Common Options Class
    '''
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    def __getattr__(self, option):
        return None