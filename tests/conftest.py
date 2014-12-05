# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""
import os

import pytest
from webtest import TestApp

from dash.settings import TestConfig
from dash.app import create_app
from dash.database import db as _db

from .factories import (
    UserFactory,
    CampusFactory,
    DepartmentFactory,
    SubjectFactory,
    CourseFactory,
    CourseHourFactory,
)


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
    campuses = [
        CampusFactory(name="HYU Seoul", code="H0002256"),
        CampusFactory(name="HYU ERICA", code="Y0000316"),
    ]
    db.session.commit()
    return campuses


@pytest.fixture
def departments(db, campuses):
    hyu_seoul = campuses[0]
    _departments = [
        DepartmentFactory(
            name="Major in Computer Engineering",
            code="H0002519",
            campus=hyu_seoul,
        ),
        DepartmentFactory(
            name="Major in Computer Science",
            code="H0002518",
            campus=hyu_seoul,
        ),
        DepartmentFactory(
            name="Department of Information System",
            code="H0002867",
            campus=hyu_seoul,
        ),
        DepartmentFactory(
            name="Department of Electronic Engineering",
            code="H0002575",
            campus=hyu_seoul,
        ),
        DepartmentFactory(
            name="Department of Electrical and Bioengineering",
            code="H0002574",
            campus=hyu_seoul,
        ),
        DepartmentFactory(
            name="Department of Media Communication",
            code="H0003665",
            campus=hyu_seoul,
        ),
        DepartmentFactory(
            name="Department of Korean Language Education",
            code="H0002719",
            campus=hyu_seoul,
        ),
    ]
    db.session.commit()
    return _departments


@pytest.fixture
def subjects(db):
    _subjects = [
        SubjectFactory(
            name="Understanding Patent Law",
            code="GEN6006",
        ),
        SubjectFactory(
            name="Media Criticism",
            code="JOU4009",
        ),
        SubjectFactory(
            name="Visual Culture",
            code="JOU2012",
        ),
        SubjectFactory(
            name="Understanding The Chinese Literature",
            code="CUL0021",
        ),
        SubjectFactory(
            name="Understanding Digital Media",
            code="JMC3040",
        ),
        SubjectFactory(
            name="Signals and Systems",
            code="ECE3008",
        ),
        SubjectFactory(
            name="Understanding Literature",
            code="KLE2009",
        ),
    ]
    db.session.commit()
    return _subjects


@pytest.fixture
def courses(db, departments, subjects):
    _courses = [
        CourseFactory(
            code="10037",
            instructor="Euee S. Jang",
            credit=2.00,
            target_grade=3,
            subject=subjects[0],        # Understanding Patent Law
            department=departments[0],  # Major in Computer Engineering
        ),
        CourseFactory(
            code="15254",
            instructor="Sunny Yoon",
            credit=2.00,
            target_grade=None,
            subject=subjects[0],        # Understanding Patent Law
            department=None,
        ),
        CourseFactory(
            code="11552",
            instructor="Sunny Yoon",
            credit=3.00,
            target_grade=3,
            subject=subjects[1],        # Media Criticism
            department=departments[5],  # Department of Media Communication
        ),
        CourseFactory(
            code="12798",
            instructor="Sunny Yoon",
            credit=3.00,
            target_grade=2,
            subject=subjects[2],        # Visual Culture
            department=departments[5],  # Department of Media Communication
        ),
        CourseFactory(
            code="15002",
            instructor="Park Eun Jung",
            credit=2.00,
            target_grade=None,
            subject=subjects[3],        # Understanding The Chinese Literature
            department=None,
        ),
        CourseFactory(
            code="11543",
            instructor="Kim Soochul",
            credit=3.00,
            target_grade=3,
            subject=subjects[4],        # Understanding Digital Media
            department=departments[5],  # Department of Media Communication
        ),
        CourseFactory(
            code="11615",
            instructor="Lee Sang Hwa",
            credit=3.00,
            target_grade=2,
            subject=subjects[5],        # Signals and Systems
            department=departments[0],  # Major in Computer Engineering
        ),
        CourseFactory(
            code="11970",
            instructor="Cho Eun Pa",
            credit=2.00,
            target_grade=1,
            subject=subjects[6],        # Understanding Literature
            department=departments[6],  # Department of Korean Language
                                        # Education
        ),
    ]

    c = _courses[0]
    CourseHourFactory(
        day_of_week=1,
        start_time=5,
        end_time=8,
        course=c,
    )

    c = _courses[1]
    CourseHourFactory(
        day_of_week=3,
        start_time=17,
        end_time=20,
        course=c,
    )

    c = _courses[2]
    CourseHourFactory(
        day_of_week=2,
        start_time=11,
        end_time=13,
        course=c,
    )
    CourseHourFactory(
        day_of_week=4,
        start_time=11,
        end_time=13,
        course=c,
    )

    c = _courses[3]
    CourseHourFactory(
        day_of_week=2,
        start_time=15,
        end_time=17,
        course=c,
    )
    CourseHourFactory(
        day_of_week=4,
        start_time=15,
        end_time=17,
        course=c,
    )

    c = _courses[4]
    CourseHourFactory(
        day_of_week=3,
        start_time=15,
        end_time=18,
        course=c,
    )

    c = _courses[5]
    CourseHourFactory(
        day_of_week=0,
        start_time=13,
        end_time=15,
        course=c,
    )
    CourseHourFactory(
        day_of_week=0,
        start_time=16,
        end_time=18,
        course=c,
    )

    c = _courses[6]
    CourseHourFactory(
        day_of_week=1,
        start_time=11,
        end_time=13,
        course=c,
    )
    CourseHourFactory(
        day_of_week=3,
        start_time=3,
        end_time=5,
        course=c,
    )

    c = _courses[7]
    CourseHourFactory(
        day_of_week=0,
        start_time=11,
        end_time=14,
        course=c,
    )

    db.session.commit()
    return _courses
