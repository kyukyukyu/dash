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
    CourseFactory,
    GeneralCourseFactory,
    CourseClassFactory,
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
        DepartmentFactory(
            name="Classics in Humanities : Skill in Reading",
            code="H0003886",
            campus=hyu_seoul,
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
        SubjectFactory(
            name="Classics in Humanities : Skill in Reading",
            code="CLS1013",
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
        CourseFactory(
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
            subject=subjects[0],                        # Understanding Patent Law
            gen_edu_category=gen_edu_categories[0],     # Business and Leadership
            departments=[departments[7]],               # College
        ),
        CourseFactory(
            code="11552",
            instructor="Sunny Yoon",
            credit=3.00,
            target_grade=3,
            subject=subjects[1],            # Media Criticism
            departments=[departments[5]],   # Department of Media Communication
        ),
        CourseFactory(
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
            gen_edu_category=gen_edu_categories[1],     # Liberal Arts
            departments=[departments[7]],       # College
        ),
        CourseFactory(
            code="11543",
            instructor="Kim Soochul",
            credit=3.00,
            target_grade=3,
            subject=subjects[4],            # Understanding Digital Media
            departments=[departments[5]],   # Department of Media Communication
        ),
        CourseFactory(
            code="11615",
            instructor="Lee Sang Hwa",
            credit=3.00,
            target_grade=2,
            subject=subjects[5],            # Signals and Systems
            departments=[departments[0]],   # Major in Computer Engineering
        ),
        CourseFactory(
            code="11970",
            instructor="Cho Eun Pa",
            credit=2.00,
            target_grade=1,
            subject=subjects[6],            # Understanding Literature
            departments=[departments[6]],   # Department of Korean Language
                                            # Education
        ),
        CourseFactory(
            code="22294",
            instructor="Kim, Sang-jean",
            credit=3.00,
            target_grade=3,
            subject=subjects[7],            # Understanding Classical Poetry
            departments=[departments[8]],   # Department of Korean Language &
                                            # Literature
        ),
        CourseFactory(
            code="22361",
            instructor="Lee, Hee-soo",
            credit=3.00,
            target_grade=4,
            subject=subjects[8],            # Understanding Middle East and
                                            # Islamic World
            departments=[departments[9]],   # Department of Cultural Anthropology
        ),
        CourseFactory(
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
            gen_edu_category=gen_edu_categories[2],     # Language and World Culture
            departments=[departments[10]],      # College
        ),
        GeneralCourseFactory(
            code="20016",
            instructor="Suk Dongwoo",
            credit=2.00,
            subject=subjects[11],       # History of The Earth
            gen_edu_category=gen_edu_categories[3],     # Science Technology and
                                                # Environment
            departments=[departments[10]],      # College
        ),
        GeneralCourseFactory(
            major=True,
            code="15007",
            instructor="Jeon Eunjin",
            credit=3.00,
            subject=subjects[12],   # Classics in Humanities : Skill in Reading
            gen_edu_category=gen_edu_categories[1],     # Liberal Arts
            departments=[departments[7],    # College
                         departments[11]],  # Division of Reading Classics
        )
    ]

    c = _courses[0]
    CourseClassFactory(
        day_of_week=1,
        start_period=5,
        end_period=8,
        course=c,
    )

    c = _courses[1]
    CourseClassFactory(
        day_of_week=3,
        start_period=17,
        end_period=20,
        course=c,
    )

    c = _courses[2]
    CourseClassFactory(
        day_of_week=2,
        start_period=11,
        end_period=13,
        course=c,
    )
    CourseClassFactory(
        day_of_week=4,
        start_period=11,
        end_period=13,
        course=c,
    )

    c = _courses[3]
    CourseClassFactory(
        day_of_week=2,
        start_period=15,
        end_period=17,
        course=c,
    )
    CourseClassFactory(
        day_of_week=4,
        start_period=15,
        end_period=17,
        course=c,
    )

    c = _courses[4]
    CourseClassFactory(
        day_of_week=3,
        start_period=15,
        end_period=18,
        course=c,
    )

    c = _courses[5]
    CourseClassFactory(
        day_of_week=0,
        start_period=13,
        end_period=15,
        course=c,
    )
    CourseClassFactory(
        day_of_week=0,
        start_period=16,
        end_period=18,
        course=c,
    )

    c = _courses[6]
    CourseClassFactory(
        day_of_week=1,
        start_period=11,
        end_period=13,
        course=c,
    )
    CourseClassFactory(
        day_of_week=3,
        start_period=3,
        end_period=5,
        course=c,
    )

    c = _courses[7]
    CourseClassFactory(
        day_of_week=0,
        start_period=11,
        end_period=14,
        course=c,
    )

    c = _courses[8]
    CourseClassFactory(
        day_of_week=0,
        start_period=10,
        end_period=12,
        course=c,
    )
    CourseClassFactory(
        day_of_week=1,
        start_period=4,
        end_period=6,
        course=c,
    )

    c = _courses[9]
    CourseClassFactory(
        day_of_week=1,
        start_period=16,
        end_period=18,
        course=c,
    )
    CourseClassFactory(
        day_of_week=3,
        start_period=6,
        end_period=8,
        course=c,
    )

    c = _courses[10]
    CourseClassFactory(
        day_of_week=3,
        start_period=5,
        end_period=7,
        course=c,
    )
    CourseClassFactory(
        day_of_week=3,
        start_period=8,
        end_period=10,
        course=c,
    )

    c = _courses[11]
    CourseClassFactory(
        day_of_week=3,
        start_period=15,
        end_period=18,
        course=c,
    )

    c = _courses[12]
    CourseClassFactory(
        day_of_week=2,
        start_period=5,
        end_period=8,
        course=c,
    )

    c = _courses[13]
    CourseClassFactory(
        day_of_week=4,
        start_period=9,
        end_period=11,
        course=c,
    )
    CourseClassFactory(
        day_of_week=4,
        start_period=12,
        end_period=14,
        course=c,
    )

    db.session.commit()
    return _courses
