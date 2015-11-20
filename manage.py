#!/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib
import os
import sys
import subprocess
from flask.ext.script import Manager, Shell, Server
from flask.ext.migrate import MigrateCommand

from dash.app import create_app
from dash.catalog.models import Campus
from dash.user.models import User
from dash.settings import DevConfig, ProdConfig
from dash.database import db

if os.environ.get("DASH_ENV") == 'prod':
    app = create_app(ProdConfig)
else:
    app = create_app(DevConfig)

manager = Manager(app)
TEST_CMD = "py.test tests"


def _make_context():
    """Return context dict for a shell session so you can access
    app, db, and the User model by default.
    """
    return {'app': app, 'db': db, 'User': User}


@manager.command
def test():
    """Run the tests."""
    import pytest
    exit_code = pytest.main(['tests', '--verbose'])
    return exit_code


@manager.option('-c', '--code', dest='campus_code')
def update_catalog(campus_code):
    """Updates catalog of a campus using user-written scraper."""
    campus = Campus.query.filter_by(code=campus_code)
    scraper = importlib.import_module(campus.scraper)
    scraper.update(campus)

manager.add_command('server', Server())
manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
