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
    Course,
    Department,
    Lecture,
    LectureHour,
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


class CourseFactory(BaseFactory):
    name = Sequence(lambda n: "course{0}".format(n))
    code = FuzzyText(length=7)

    class Meta:
        model = Course


class LectureFactory(BaseFactory):
    name = Sequence(lambda n: "course{0}".format(n))
    code = FuzzyText(length=5)
    instructor = FuzzyText(length=10)
    credit = FuzzyFloat(1.0, 6.0)
    target_grade = FuzzyInteger(1, 5)
    course = SubFactory(CourseFactory)
    department = SubFactory(DepartmentFactory)

    class Meta:
        model = Lecture

    @post_generation
    def hours(self, create, extracted, **kwargs):
        _hours = []

        if extracted:
            for l_h in extracted:
                l_h.lecture = self
                _hours.append(l_h)
        else:
            while len(_hours) < 2:
                l_h =  LectureHourFactory.build(lecture=self)

                if any(l_h.conflicts_with(h) for h in _hours):
                    continue

                if create:
                    l_h.save()

                _hours.append(l_h)

        return _hours


class LectureHourFactory(BaseFactory):
    day_of_week = FuzzyInteger(0, 6)
    start_time = FuzzyInteger(1, 8)
    end_time = LazyAttribute(lambda o: o.start_time + 3)
    lecture = SubFactory(LectureFactory)

    class Meta:
        model = LectureHour
