# -*- coding: utf-8 -*-
"""Scraper unit tests."""
import operator

import pytest

from dash.catalog.models import (
    Department,
    Subject,
    GenEduCategory,
    GeneralCourse,
    MajorCourse,
)
from dash.catalog.scraper import update_catalog
from .factories import (
    CampusFactory,
    DepartmentFactory,
    SubjectFactory,
    GenEduCategoryFactory,
    GeneralCourseFactory,
    MajorCourseFactory,
)


@pytest.mark.usefixtures('db')
class TestScraper(object):

    def test_update_catalog_when_empty(self, db):
        campus = CampusFactory()
        departments = []
        subjects = []
        gen_edu_categories = []
        major_courses = []
        general_courses = []

        with update_catalog(campus) as catalog:
            departments.append(DepartmentFactory.build(name='CSE CS',
                                                       campus=None))
            departments.append(DepartmentFactory.build(name='ECE',
                                                       campus=None))
            departments.append(DepartmentFactory.build(name='CSE SW',
                                                       campus=None))
            departments.append(DepartmentFactory.build(name='Undergraduate',
                                                       campus=None))
            catalog.hold_departments(departments)

            subjects.append(SubjectFactory.build(name='Software Engineering'))
            subjects.append(SubjectFactory.build(name='Computer Architecture'))
            subjects.append(
                SubjectFactory.build(name='Creativity and Communication'))
            catalog.hold_subjects(subjects)

            gen_edu_categories.append(
                GenEduCategoryFactory.build(name='Science and Technology'))
            catalog.hold_gen_edu_categories(gen_edu_categories)

            major_courses.append(
                MajorCourseFactory.build(subject=subjects[0],
                                         departments=[departments[0]]))
            major_courses.append(
                MajorCourseFactory.build(subject=subjects[0],
                                         departments=[departments[0],
                                                      departments[2]]))
            major_courses.append(
                MajorCourseFactory.build(subject=subjects[1],
                                         departments=[departments[0]]))
            major_courses.append(
                MajorCourseFactory.build(subject=subjects[1],
                                         departments=[departments[1]]))
            catalog.hold_courses(major_courses)

            general_courses.append(
                GeneralCourseFactory.build(subject=subjects[2],
                                           category=gen_edu_categories[0],
                                           departments=[departments[3]]))

            catalog.hold_courses(general_courses)

        # Rollback required here to ensure that scraper context manager
        # works as expected.
        db.session.rollback()

        for Model, mock_objs in ((Department, departments),
                                 (Subject, subjects),
                                 (GenEduCategory, gen_edu_categories),
                                 (MajorCourse, major_courses),
                                 (GeneralCourse, general_courses)):
            mock_objs_sorted = sorted(mock_objs,
                                      key=operator.attrgetter('code'))
            stored_objs = Model.query.order_by(Model.code).all()
            assert len(mock_objs_sorted) == len(stored_objs)
            assert all(m is s for m, s in zip(mock_objs_sorted, stored_objs))

        # Test relationships between departments and courses
        d = departments[0]
        assert major_courses[0] in d.courses
        assert major_courses[1] in d.courses
        assert major_courses[2] in d.courses
        d = departments[1]
        assert major_courses[3] in d.courses
        d = departments[2]
        assert major_courses[1] in d.courses
        d = departments[3]
        assert general_courses[0] in d.courses
