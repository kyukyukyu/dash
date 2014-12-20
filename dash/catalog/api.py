# -*- coding: utf-8 -*-
from functools import wraps
from collections import Mapping
from six import iteritems, text_type
from sqlalchemy.orm.exc import NoResultFound
from flask import Blueprint, render_template, abort
from flask.ext.login import login_required
from flask.ext.restful import (
    Resource,
    reqparse,
    fields,
    marshal,
)

from dash.catalog import models
from dash.database import db
from dash.extensions import api


def extend(dst, *args):
    extended = dst.copy()
    for d in args:
        if not isinstance(d, Mapping):
            raise TypeError('arguments should be mappings')
        for k, v in iteritems(d):
            extended[k] = v
    return extended


entity_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'created_at': fields.DateTime(dt_format='iso8601'),
}

department_fields = extend(entity_fields, {
    'name': fields.String,
    'campus_id': fields.Integer,
})

campus_fields = extend(entity_fields, {
    'name': fields.String,
    'departments': fields.List(fields.Nested(department_fields))
})

subject_fields = extend(entity_fields, {
    'name': fields.String,
})

course_hour_fields = {
    'id': fields.Integer,
    'day_of_week': fields.Integer,
    'start_time': fields.Integer,
    'end_time': fields.Integer,
}

course_fields = extend(entity_fields, {
    'type': fields.String,
    'instructor': fields.String,
    'credit': fields.Float,
    'subject_id': fields.Integer,
    'subject': fields.Nested(subject_fields),
    'department_id': fields.Integer,
    'department': fields.Nested(department_fields),
    'hours': fields.List(fields.Nested(course_hour_fields)),
})

gen_edu_category_fields = extend(entity_fields, {
    'name': fields.String,
})


class ResourceWithQuery(Resource):
    model = None
    fields = None

    @classmethod
    def query(cls, **kwargs):
        return db.session.query(cls.model)

    @classmethod
    def marshal(cls, data):
        return marshal(data, cls.fields)


class Entity(ResourceWithQuery):
    def get(self, **kwargs):
        id = kwargs['id']
        id_column = self.model.id
        try:
            entity = self.query(**kwargs).filter(id_column == id).one()
            return self.marshal(entity), 200
        except NoResultFound:
            abort(404)


def like_filter_criterion(column, keyword, case_sensitive=False):
    criterion_func = column.ilike if not case_sensitive else column.like

    for word in keyword.split():
        yield criterion_func("%{}%".format(word))


class Collection(ResourceWithQuery):
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int)
    parser.add_argument('results_per_page', type=int)

    @classmethod
    def query(cls, **kwargs):
        return super(Collection, cls).query(**kwargs).order_by(cls.model.id)

    def get(self, **kwargs):
        args = self.parser.parse_args()
        page = args.get('page') or 1

        query = self.query(**kwargs)
        pagination = query.paginate(
            page,
            per_page=args.get('results_per_page') or 20,
        )

        ret_objects = [self.marshal(item) for item in pagination.items]
        return {
            'num_results': pagination.total,
            'page': page,
            'num_pages': pagination.pages,
            'objects': ret_objects,
        }, 200


def when(variable, query_processor, **query_processors):
    """A decorator for subclasses of :class:`dash.catalog.api.QueryMixin`
    which enables query processing according to existence of variables of URL
    routing rule.

    :param variable: Name of variable in URL routing rule.
    :param query_processor: Function which processes
                            :class:`sqlalchemy.orm.query.Query` object. This
                            function should accept a
                            :class:`sqlalchemy.orm.query.Query` object and the
                            value of variable as arguments, and return a
                            :class:`sqlalchemy.orm.query.Query` object.
    :param query_processors: Keyword arguments of which the key is name of
                             variable in URL routing rule, and the value is
                             query processor function for the variable.
    """
    def decorator(cls):
        query_processors.update([(variable, query_processor)])

        def query_decorator(f):
            @wraps(f)
            def wrapper(kls, *args, **kwargs):
                query = f(*args, **kwargs)
                for v, p in iteritems(query_processors):
                    if v in kwargs:
                        query = p(query, kwargs[v])
                return query
            return wrapper

        cls.query = classmethod(query_decorator(cls.query))
        return cls

    return decorator


class CampusMixin(object):
    model = models.Campus
    fields = campus_fields


class Campus(CampusMixin, Entity):
    pass


class CampusList(CampusMixin, Collection):
    pass

qp_department_campus_id = lambda q, v: q.filter(models.Department.campus_id == v)


class DepartmentMixin(object):
    model = models.Department
    fields = department_fields


@when('campus_id', qp_department_campus_id)
class Department(DepartmentMixin, Entity):
    pass


@when('campus_id', qp_department_campus_id)
class DepartmentList(DepartmentMixin, Collection):
    pass


class SubjectMixin(object):
    model = models.Subject
    fields = subject_fields


class Subject(SubjectMixin, Entity):
    pass


class SubjectList(SubjectMixin, Collection):
    pass


class GenEduCategoryMixin(object):
    model = models.GenEduCategory
    fields = gen_edu_category_fields


class GenEduCategory(GenEduCategoryMixin, Entity):
    pass


class GenEduCategoryList(GenEduCategoryMixin, Collection):
    pass


qp_course_campus_id = lambda q, v: q.join(CourseMixin.model.department) \
    .filter(models.Department.campus_id == v)


class CourseMixin(ResourceWithQuery):
    model = db.with_polymorphic(models.Course,
                                [models.GeneralCourse, models.MajorCourse])
    general_fields = extend(course_fields, {
        'category_id': fields.Integer,
        'category': fields.Nested(gen_edu_category_fields),
    })
    major_fields = extend(course_fields, {
        'target_grade': fields.Integer,
    })
    fields_by_model = {
        models.GeneralCourse: general_fields,
        models.MajorCourse: major_fields,
    }

    @classmethod
    def query(cls, **kwargs):
        return super(CourseMixin, cls).query(**kwargs) \
            .join(cls.model.subject) \
            .options(db.contains_eager(cls.model.subject))

    @classmethod
    def marshal(cls, data):
        try:
            fields = cls.fields_by_model[type(data)]
        except KeyError:
            raise TypeError('type of data is invalid')
        return marshal(data, fields)


@when('campus_id', qp_course_campus_id)
class Course(CourseMixin, Entity):
    pass


@when('campus_id', qp_course_campus_id)
class CourseList(CourseMixin, Collection):
    parser = Collection.parser.copy()
    parser.add_argument('name', type=text_type)
    parser.add_argument('subject_code', type=text_type)
    parser.add_argument('instructor', type=text_type)
    parser.add_argument('type', type=text_type)
    parser.add_argument('category_id', type=int)
    parser.add_argument('target_grade', type=int)
    parser.add_argument('department_id', type=int)

    @classmethod
    def query(cls, **kwargs):
        q = super(CourseList, cls).query(**kwargs)
        entity = cls.model
        args = cls.parser.parse_args()

        attrs_for_eq = []
        course_type = args.get('type')
        if course_type == 'general':
            q = q.filter(entity.type == models.GeneralCourse.TYPE)
            attrs_for_eq.append(
                ('category_id', entity.GeneralCourse.category_id)
            )
        elif course_type == 'major':
            q = q.filter(entity.type == models.MajorCourse.TYPE)
            attrs_for_eq.extend([
                ('department_id', entity.MajorCourse.department_id),
                ('target_grade', entity.MajorCourse.target_grade),
            ])

        for argname in ('name', 'subject_code', 'instructor'):
            argval = args.get(argname)
            if argval:
                column = getattr(cls.model, argname)
                q = q.filter(*like_filter_criterion(column, argval))

        for argname, column in attrs_for_eq:
            argval = args.get(argname)
            if argval:
                q = q.filter(column == argval)

        return q

api.add_resource(Campus, '/campuses/<int:id>')
api.add_resource(CampusList, '/campuses')
api.add_resource(Department,
                 '/departments/<int:id>',
                 '/campuses/<int:campus_id>/departments/<int:id>')
api.add_resource(DepartmentList,
                 '/departments',
                 '/campuses/<int:campus_id>/departments')
api.add_resource(Subject, '/subjects/<int:id>')
api.add_resource(SubjectList, '/subjects')
api.add_resource(GenEduCategory, '/gen_edu_categories/<int:id>')
api.add_resource(GenEduCategoryList, '/gen_edu_categories')
api.add_resource(Course,
                 '/courses/<int:id>',
                 '/campuses/<int:campus_id>/courses/<int:id>')
api.add_resource(CourseList,
                 '/courses',
                 '/campuses/<int:campus_id>/courses')
