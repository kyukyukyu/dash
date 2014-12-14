# -*- coding: utf-8 -*-
"""Model unit tests."""
import datetime as dt

import pytest

from dash.user.models import User, Role
from dash.catalog.models import (
    Campus,
    Department,
    Subject,
    Course,
    GenEduCategory,
    GeneralCourse,
    MajorCourse,
    CourseHour,
)
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

        subject = Subject(code='CSE4006', name='Software Engineering')
        subject.save()

        retrieved_subject = Subject.get_by_id(subject.id)
        assert retrieved_subject == subject

        gen_edu_category = GenEduCategory(code='B4',
                                          name='Business and Leadership')
        gen_edu_category.save()

        retrieved_category = GenEduCategory.get_by_id(gen_edu_category.id)
        assert retrieved_category == gen_edu_category

        course = GeneralCourse(code='10020', subject=subject, credit=3.0,
                               department=department)
        course.category = gen_edu_category
        course.save()

        retrieved_course = Course.get_by_id(course.id)
        assert isinstance(retrieved_course, GeneralCourse)
        assert retrieved_course == course

        course2 = MajorCourse(code='10020', subject=subject,
                              department=department, credit=3.0,
                              target_grade=3)
        course2.save()

        retrieved_course = Course.get_by_id(course2.id)
        assert isinstance(retrieved_course, MajorCourse)
        assert retrieved_course == course2

        course_hour = CourseHour(day_of_week=2, start_time=14, end_time=17,
                                 course=course)
        course_hour.save()

        retrieved_course_hour = CourseHour.get_by_id(course_hour.id)
        assert retrieved_course_hour == course_hour

    def test_course_hour_conflicts_with(self):
        c_h1 = CourseHourFactory(day_of_week=1, start_time=2, end_time=5)
        c_h2 = CourseHourFactory(day_of_week=1, start_time=4, end_time=10)
        c_h3 = CourseHourFactory(day_of_week=1, start_time=6, end_time=9)
        c_h4 = CourseHourFactory(day_of_week=2, start_time=6, end_time=9)

        assert c_h1.conflicts_with(c_h2) and c_h2.conflicts_with(c_h1)
        assert not c_h1.conflicts_with(c_h3) and not c_h3.conflicts_with(c_h1)
        assert c_h2.conflicts_with(c_h3) and c_h3.conflicts_with(c_h2)
        assert all((
            not c_h1.conflicts_with(c_h4) and not c_h4.conflicts_with(c_h1),
            not c_h2.conflicts_with(c_h4) and not c_h4.conflicts_with(c_h2),
            not c_h3.conflicts_with(c_h4) and not c_h4.conflicts_with(c_h3),
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

        subject = SubjectFactory()
        db.session.commit()
        assert bool(subject.name)
        assert bool(subject.code)
        assert bool(subject.created_at)

        gen_edu_category = GenEduCategoryFactory()
        db.session.commit()
        assert bool(gen_edu_category.name)
        assert bool(gen_edu_category.code)
        assert bool(gen_edu_category.created_at)

        def assert_course(course):
            assert bool(course.code)
            assert bool(course.created_at)
            assert bool(course.instructor)
            assert bool(course.credit)
            assert bool(course.subject)
            assert course in course.subject.courses
            assert bool(course.subject_id)
            assert bool(course.department)
            assert course in course.department.courses
            assert bool(course.department_id)
            assert bool(course.campus)
            assert course in course.campus.courses

        general_course = GeneralCourseFactory()
        db.session.commit()
        assert_course(general_course)
        assert bool(general_course.category)
        assert general_course in general_course.category.courses
        assert bool(general_course.category_id)

        major_course = MajorCourseFactory()
        db.session.commit()
        assert_course(major_course)
        assert bool(major_course.target_grade)

        course_hour = CourseHourFactory()
        db.session.commit()
        assert bool(course_hour.created_at)
        assert 0 <= course_hour.day_of_week < 7
        assert course_hour.start_time >= 0
        assert course_hour.end_time >= 0
        assert bool(course_hour.course)
        assert course_hour in course_hour.course.hours
        assert bool(course_hour.course_id)
