# -*- coding: utf-8 -*-
import numbers
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
    CourseClass,
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

    @post_generation
    def classes(self, create, extracted, **kwargs):
        _classes = []

        if extracted:
            for c_c in extracted:
                c_c.course = self
                _classes.append(c_c)

        return _classes

    @post_generation
    def departments(obj, create, extracted, **kwargs):
        _departments = []

        if extracted is None:
            extracted = 2

        if isinstance(extracted, numbers.Integral):
            # Create department entities of given number.
            i = extracted
            while i > 0:
                if create:
                    department = DepartmentFactory.create()
                else:
                    department = DepartmentFactory.build()
                _departments.append(department)
                i -= 1
        else:
            # Link given departments to this course entity.
            _departments[:] = extracted

        for d in _departments:
            d.courses.append(obj)

        return _departments


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


class CourseClassFactory(BaseFactory):
    day_of_week = FuzzyInteger(0, 6)
    start_time = FuzzyInteger(1, 8)
    end_time = LazyAttribute(lambda o: o.start_time + 3)
    course = SubFactory(MajorCourseFactory)

    class Meta:
        model = CourseClass
