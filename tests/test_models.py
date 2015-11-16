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
    CourseClass,
)
from .factories import (
    UserFactory,
    CampusFactory,
    DepartmentFactory,
    SubjectFactory,
    GenEduCategoryFactory,
    GeneralCourseFactory,
    MajorCourseFactory,
    CourseClassFactory,
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
                               departments=[department])
        course.category = gen_edu_category
        course.save()

        retrieved_course = Course.get_by_id(course.id)
        assert isinstance(retrieved_course, GeneralCourse)
        assert retrieved_course == course

        course2 = MajorCourse(code='10020', subject=subject,
                              departments=[department], credit=3.0,
                              target_grade=3)
        course2.save()

        retrieved_course = Course.get_by_id(course2.id)
        assert isinstance(retrieved_course, MajorCourse)
        assert retrieved_course == course2

        course_class = CourseClass(day_of_week=2, start_period=14,
                                   end_period=17, course=course)
        course_class.save()

        retrieved_course_class = CourseClass.get_by_id(course_class.id)
        assert retrieved_course_class == course_class

    def test_course_class_conflicts_with(self):
        c_c1 = CourseClassFactory(day_of_week=1, start_period=2, end_period=5)
        c_c2 = CourseClassFactory(day_of_week=1, start_period=4, end_period=10)
        c_c3 = CourseClassFactory(day_of_week=1, start_period=6, end_period=9)
        c_c4 = CourseClassFactory(day_of_week=2, start_period=6, end_period=9)

        assert c_c1.conflicts_with(c_c2) and c_c2.conflicts_with(c_c1)
        assert not c_c1.conflicts_with(c_c3) and not c_c3.conflicts_with(c_c1)
        assert c_c2.conflicts_with(c_c3) and c_c3.conflicts_with(c_c2)
        assert all((
            not c_c1.conflicts_with(c_c4) and not c_c4.conflicts_with(c_c1),
            not c_c2.conflicts_with(c_c4) and not c_c4.conflicts_with(c_c2),
            not c_c3.conflicts_with(c_c4) and not c_c4.conflicts_with(c_c3),
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
            assert bool(course.name)
            assert course.name == course.subject.name
            assert bool(course.departments)
            for d in course.departments:
                assert course in d.courses

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

        course_class = CourseClassFactory()
        db.session.commit()
        assert bool(course_class.created_at)
        assert 0 <= course_class.day_of_week < 7
        assert course_class.start_period >= 0
        assert course_class.end_period >= 0
        assert bool(course_class.course)
        assert course_class in course_class.course.classes
        assert bool(course_class.course_id)
