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
    GenEduCategoryFactory,
    GeneralCourseFactory,
    MajorCourseFactory,
    CourseHourFactory,
)


@pytest.yield_fixture(scope='function')
def app():
    _app = create_app(TestConfig)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope='function')
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


@pytest.fixture(scope='function')
def campuses(db):
    campuses = [
        CampusFactory(name="HYU Seoul", code="H0002256"),
        CampusFactory(name="HYU ERICA", code="Y0000316"),
    ]
    db.session.commit()
    return campuses


@pytest.fixture(scope='function')
def departments(db, campuses):
    hyu_seoul = campuses[0]
    hyu_erica = campuses[1]
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
        DepartmentFactory(
            name="College",
            code="H0002256",
            campus=hyu_seoul,
        ),
        DepartmentFactory(
            name="Department of Korean Language & Literature",
            code="Y0000452",
            campus=hyu_erica,
        ),
        DepartmentFactory(
            name="Department of Cultural Anthropology",
            code="Y0000467",
            campus=hyu_erica,
        ),
        DepartmentFactory(
            name="College",
            code="Y0000316",
            campus=hyu_erica,
        ),
    ]
    db.session.commit()
    return _departments


@pytest.fixture(scope='function')
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
        SubjectFactory(
            name="Understanding Classical Poetry",
            code="KOR3043",
        ),
        SubjectFactory(
            name="Understanding Middle East and Islamic World",
            code="ANT4034",
        ),
        SubjectFactory(
            name="Dynamics in the Korean Language",
            code="KOR1011",
        ),
        SubjectFactory(
            name="Understanding of the Third World Culture",
            code="CUL0092",
        ),
        SubjectFactory(
            name="History of The Earth",
            code="CUL2076",
        ),
    ]
    db.session.commit()
    return _subjects


@pytest.fixture(scope='function')
def gen_edu_categories(db):
    _categories = [
        GenEduCategoryFactory(
            code="B4",
            name="Business and Leadership",
        ),
        GenEduCategoryFactory(
            code="B1",
            name="Liberal Arts",
        ),
        GenEduCategoryFactory(
            code="E5",
            name="Language and World Culture",
        ),
        GenEduCategoryFactory(
            code="E3",
            name="Science Technology and Environment",
        ),
    ]
    db.session.commit()
    return _categories


@pytest.fixture(scope='function')
def courses(db, departments, subjects, gen_edu_categories):
    # There is a rule for fixture data that codes of courses from HYU Seoul
    # start with "1", and ones from HYU ERICA starts with "2".
    _courses = [
        MajorCourseFactory(
            code="10037",
            instructor="Euee S. Jang",
            credit=2.00,
            target_grade=3,
            subject=subjects[0],            # Understanding Patent Law
            departments=[departments[0]],   # Major in Computer Engineering
        ),
        GeneralCourseFactory(
            code="15254",
            instructor="Sunny Yoon",
            credit=2.00,
            subject=subjects[0],                # Understanding Patent Law
            category=gen_edu_categories[0],     # Business and Leadership
            departments=[departments[7]],       # College
        ),
        MajorCourseFactory(
            code="11552",
            instructor="Sunny Yoon",
            credit=3.00,
            target_grade=3,
            subject=subjects[1],            # Media Criticism
            departments=[departments[5]],   # Department of Media Communication
        ),
        MajorCourseFactory(
            code="12798",
            instructor="Sunny Yoon",
            credit=3.00,
            target_grade=2,
            subject=subjects[2],            # Visual Culture
            departments=[departments[5]],   # Department of Media Communication
        ),
        GeneralCourseFactory(
            code="15002",
            instructor="Park Eun Jung",
            credit=2.00,
            subject=subjects[3],        # Understanding The Chinese Literature
            category=gen_edu_categories[1],     # Liberal Arts
            departments=[departments[7]],       # College
        ),
        MajorCourseFactory(
            code="11543",
            instructor="Kim Soochul",
            credit=3.00,
            target_grade=3,
            subject=subjects[4],            # Understanding Digital Media
            departments=[departments[5]],   # Department of Media Communication
        ),
        MajorCourseFactory(
            code="11615",
            instructor="Lee Sang Hwa",
            credit=3.00,
            target_grade=2,
            subject=subjects[5],            # Signals and Systems
            departments=[departments[0]],   # Major in Computer Engineering
        ),
        MajorCourseFactory(
            code="11970",
            instructor="Cho Eun Pa",
            credit=2.00,
            target_grade=1,
            subject=subjects[6],            # Understanding Literature
            departments=[departments[6]],   # Department of Korean Language
                                            # Education
        ),
        MajorCourseFactory(
            code="22294",
            instructor="Kim, Sang-jean",
            credit=3.00,
            target_grade=3,
            subject=subjects[7],            # Understanding Classical Poetry
            departments=[departments[8]],   # Department of Korean Language &
                                            # Literature
        ),
        MajorCourseFactory(
            code="22361",
            instructor="Lee, Hee-soo",
            credit=3.00,
            target_grade=4,
            subject=subjects[8],            # Understanding Middle East and
                                            # Islamic World
            departments=[departments[9]],   # Department of Cultural Anthropology
        ),
        MajorCourseFactory(
            code="22291",
            instructor="Kim, Zong-su",
            credit=3.00,
            target_grade=3,
            subject=subjects[9],            # Dynamics in the Korean Language
            departments=[departments[8]],   # Department of Korean Language &
                                            # Literature
        ),
        GeneralCourseFactory(
            code="20025",
            instructor="Kang, Kyoung-ran",
            credit=2.00,
            subject=subjects[10],       # Understanding of the Third World
                                        # Culture
            category=gen_edu_categories[2],     # Language and World Culture
            departments=[departments[10]],      # College
        ),
        GeneralCourseFactory(
            code="20016",
            instructor="Suk Dongwoo",
            credit=2.00,
            subject=subjects[11],       # History of The Earth
            category=gen_edu_categories[3],     # Science Technology and
                                                # Environment
            departments=[departments[10]],      # College
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

    c = _courses[8]
    CourseHourFactory(
        day_of_week=0,
        start_time=10,
        end_time=12,
        course=c,
    )
    CourseHourFactory(
        day_of_week=1,
        start_time=4,
        end_time=6,
        course=c,
    )

    c = _courses[9]
    CourseHourFactory(
        day_of_week=1,
        start_time=16,
        end_time=18,
        course=c,
    )
    CourseHourFactory(
        day_of_week=3,
        start_time=6,
        end_time=8,
        course=c,
    )

    c = _courses[10]
    CourseHourFactory(
        day_of_week=3,
        start_time=5,
        end_time=7,
        course=c,
    )
    CourseHourFactory(
        day_of_week=3,
        start_time=8,
        end_time=10,
        course=c,
    )

    c = _courses[11]
    CourseHourFactory(
        day_of_week=3,
        start_time=15,
        end_time=18,
        course=c,
    )

    c = _courses[12]
    CourseHourFactory(
        day_of_week=2,
        start_time=5,
        end_time=8,
        course=c,
    )

    db.session.commit()
    return _courses
