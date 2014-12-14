# -*- coding: utf-8 -*-
from factory import (
    LazyAttribute,
    PostGenerationMethodCall,
    Sequence,
    SubFactory,
    post_generation,
)
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyText, FuzzyFloat, FuzzyInteger

from dash.user.models import User
from dash.catalog.models import (
    Campus,
    Subject,
    Department,
    GenEduCategory,
    GeneralCourse,
    MajorCourse,
    CourseHour,
)
from dash.database import db


class BaseFactory(SQLAlchemyModelFactory):

    class Meta:
        abstract = True
        sqlalchemy_session = db.session


class UserFactory(BaseFactory):
    username = Sequence(lambda n: "user{0}".format(n))
    email = Sequence(lambda n: "user{0}@example.com".format(n))
    password = PostGenerationMethodCall('set_password', 'example')
    active = True

    class Meta:
        model = User


class CampusFactory(BaseFactory):
    name = Sequence(lambda n: "campus{0}".format(n))
    code = FuzzyText(length=6)

    class Meta:
        model = Campus


class DepartmentFactory(BaseFactory):
    name = Sequence(lambda n: "department{0}".format(n))
    code = FuzzyText(length=6)
    campus = SubFactory(CampusFactory)

    class Meta:
        model = Department


class SubjectFactory(BaseFactory):
    name = Sequence(lambda n: "subject{0}".format(n))
    code = FuzzyText(length=7)

    class Meta:
        model = Subject


class CourseFactory(BaseFactory):
    code = FuzzyText(length=5)
    instructor = FuzzyText(length=10)
    credit = FuzzyFloat(1.0, 6.0)
    subject = SubFactory(SubjectFactory)
    department = SubFactory(DepartmentFactory)

    @post_generation
    def hours(self, create, extracted, **kwargs):
        _hours = []

        if extracted:
            for c_h in extracted:
                c_h.course = self
                _hours.append(c_h)

        return _hours


class GenEduCategoryFactory(BaseFactory):
    name = Sequence(lambda n: "gen-edu-category{0}".format(n))
    code = FuzzyText(length=2)

    class Meta:
        model = GenEduCategory


class GeneralCourseFactory(CourseFactory):
    category = SubFactory(GenEduCategoryFactory)

    class Meta:
        model = GeneralCourse


class MajorCourseFactory(CourseFactory):
    target_grade = FuzzyInteger(1, 5)

    class Meta:
        model = MajorCourse


class CourseHourFactory(BaseFactory):
    day_of_week = FuzzyInteger(0, 6)
    start_time = FuzzyInteger(1, 8)
    end_time = LazyAttribute(lambda o: o.start_time + 3)
    course = SubFactory(MajorCourseFactory)

    class Meta:
        model = CourseHour
