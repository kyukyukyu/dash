# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""
import os

import pytest
from webtest import TestApp

from dash.settings import TestConfig
from dash.app import create_app
from dash.database import db as _db

from .factories import UserFactory, CampusFactory, DepartmentFactory


@pytest.yield_fixture(scope='function')
def app():
    _app = create_app(TestConfig)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope='session')
def testapp(app):
    """A Webtest app."""
    return TestApp(app)


@pytest.yield_fixture(scope='function')
def db(app):
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    _db.drop_all()


@pytest.fixture
def user(db):
    user = UserFactory(password='myprecious')
    db.session.commit()
    return user


@pytest.fixture
def campuses(db):
    campuses = [CampusFactory(), CampusFactory(), CampusFactory()]
    db.session.commit()
    return campuses


@pytest.fixture
def departments(db):
    departments = [
        DepartmentFactory(),
        DepartmentFactory(),
        DepartmentFactory(),
    ]
    db.session.commit()
    return departments
