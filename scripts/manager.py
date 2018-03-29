#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
sys.path.append('.')

from flask.ext.script import Manager, Shell, prompt_bool
from flask.ext.migrate import Migrate, MigrateCommand
from butler import app, db
from butler.user.models import init_user_data

migrate = Migrate(app, db)

manager = Manager(app, usage="Perform database operations")

manager.add_command('db', MigrateCommand)


@manager.command
def initdb():
    """initialize database tables"""
    db.create_all()


@manager.command
def dropdb():
    "Drops database tables"
    if prompt_bool("Are you sure you want to lose all your data"):
        db.drop_all()


@manager.command
def import_data():
    "Import butler data"
    init_user_data()


def _make_context():
    return dict(app=app, db=db)


manager.add_command("shell", Shell(make_context=_make_context))


if __name__ == '__main__':
    manager.run()
