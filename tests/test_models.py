# -*- coding: utf-8 -*-
"""Model unit tests."""
import datetime as dt

import pytest

from dash.user.models import User, Role
from dash.catalog.models import (
    Campus,
    Department,
    Course,
    Lecture,
    LectureHour,
)
from .factories import (
    UserFactory,
    CampusFactory,
    DepartmentFactory,
    CourseFactory,
    LectureFactory,
    LectureHourFactory,
)


@pytest.mark.usefixtures('db')
class TestUser:

    def test_get_by_id(self):
        user = User('foo', 'foo@bar.com')
        user.save()

        retrieved = User.get_by_id(user.id)
        assert retrieved == user

    def test_created_at_defaults_to_datetime(self):
        user = User(username='foo', email='foo@bar.com')
        user.save()
        assert bool(user.created_at)
        assert isinstance(user.created_at, dt.datetime)

    def test_password_is_nullable(self):
        user = User(username='foo', email='foo@bar.com')
        user.save()
        assert user.password is None

    def test_factory(self, db):
        user = UserFactory(password="myprecious")
        db.session.commit()
        assert bool(user.username)
        assert bool(user.email)
        assert bool(user.created_at)
        assert user.is_admin is False
        assert user.active is True
        assert user.check_password('myprecious')

    def test_check_password(self):
        user = User.create(username="foo", email="foo@bar.com",
                    password="foobarbaz123")
        assert user.check_password('foobarbaz123') is True
        assert user.check_password("barfoobaz") is False

    def test_full_name(self):
        user = UserFactory(first_name="Foo", last_name="Bar")
        assert user.full_name == "Foo Bar"

    def test_roles(self):
        role = Role(name='admin')
        role.save()
        u = UserFactory()
        u.roles.append(role)
        u.save()
        assert role in u.roles


@pytest.mark.usefixtures('db')
class TestCatalog:

    def test_get_by_id(self):
        campus = Campus(code='HYSEOUL', name='HYU Seoul')
        campus.save()

        retrieved_campus = Campus.get_by_id(campus.id)
        assert retrieved_campus == campus

        department = Department(code='H3HADD',
                                name='Division of Computer Science and '
                                     'Engineering')
        department.campus = campus
        department.save()

        retrieved_department = Department.get_by_id(department.id)
        assert retrieved_department == department

        course = Course(code='CSE4006', name='Software Engineering')
        course.save()

        retrieved_course = Course.get_by_id(course.id)
        assert retrieved_course == course

        lecture = Lecture(code='10020', name='Software Engineering',
                          course=course, department=department, credit=3.0,
                          target_grade=3)
        lecture.save()

        retrieved_lecture = Lecture.get_by_id(lecture.id)
        assert retrieved_lecture == lecture

        lecture_hour = LectureHour(day_of_week=2, start_time=14, end_time=17,
                                   lecture=lecture)
        lecture_hour.save()

        retrieved_lecture_hour = LectureHour.get_by_id(lecture_hour.id)
        assert retrieved_lecture_hour == lecture_hour

    def test_lecture_hour_conflicts_with(self):
        l_h1 = LectureHourFactory(day_of_week=1, start_time=2, end_time=5)
        l_h2 = LectureHourFactory(day_of_week=1, start_time=4, end_time=10)
        l_h3 = LectureHourFactory(day_of_week=1, start_time=6, end_time=9)
        l_h4 = LectureHourFactory(day_of_week=2, start_time=6, end_time=9)

        assert l_h1.conflicts_with(l_h2) and l_h2.conflicts_with(l_h1)
        assert not l_h1.conflicts_with(l_h3) and not l_h3.conflicts_with(l_h1)
        assert l_h2.conflicts_with(l_h3) and l_h3.conflicts_with(l_h2)
        assert all((
            not l_h1.conflicts_with(l_h4) and not l_h4.conflicts_with(l_h1),
            not l_h2.conflicts_with(l_h4) and not l_h4.conflicts_with(l_h2),
            not l_h3.conflicts_with(l_h4) and not l_h4.conflicts_with(l_h3),
        ))

    def test_factory(self, db):
        campus = CampusFactory()
        db.session.commit()
        assert bool(campus.name)
        assert bool(campus.code)
        assert bool(campus.created_at)

        department = DepartmentFactory()
        db.session.commit()
        assert bool(department.name)
        assert bool(department.code)
        assert bool(department.created_at)
        assert bool(department.campus)
        assert isinstance(department.campus, Campus)
        assert bool(department.campus_id)
        assert department in department.campus.departments

        course = CourseFactory()
        db.session.commit()
        assert bool(course.name)
        assert bool(course.code)
        assert bool(course.created_at)

        lecture = LectureFactory()
        db.session.commit()
        assert bool(lecture.name)
        assert bool(lecture.code)
        assert bool(lecture.created_at)
        assert bool(lecture.instructor)
        assert bool(lecture.credit)
        assert bool(lecture.target_grade)
        assert bool(lecture.course)
        assert lecture in lecture.course.lectures
        assert bool(lecture.course_id)
        assert bool(lecture.department)
        assert lecture in lecture.department.lectures
        assert bool(lecture.department_id)
        assert bool(lecture.campus)
        assert lecture in lecture.campus.lectures

        lecture_hour = LectureHourFactory()
        db.session.commit()
        assert bool(lecture_hour.created_at)
        assert 0 <= lecture_hour.day_of_week < 7
        assert lecture_hour.start_time >= 0
        assert lecture_hour.end_time >= 0
        assert bool(lecture_hour.lecture)
        assert lecture_hour in lecture_hour.lecture.hours
        assert bool(lecture_hour.lecture_id)
