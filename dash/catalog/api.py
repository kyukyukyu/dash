# -*- coding: utf-8 -*-
from functools import wraps
from flask import Blueprint, render_template
from collections import Mapping
from six import iteritems
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
        entity = self.query(**kwargs).filter(id_column == id).one()
        return self.marshal(entity), 200


class Collection(ResourceWithQuery):
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int)
    parser.add_argument('results_per_page', type=int)

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

qp_campus_id = lambda q, v: q.filter(models.Department.campus_id == v)


class DepartmentMixin(object):
    model = models.Department
    fields = department_fields


@when('campus_id', qp_campus_id)
class Department(DepartmentMixin, Entity):
    pass


@when('campus_id', qp_campus_id)
class DepartmentList(DepartmentMixin, Collection):
    pass


class SubjectMixin(object):
    model = models.Subject
    fields = subject_fields


class Subject(SubjectMixin, Entity):
    pass


class SubjectList(SubjectMixin, Collection):
    pass


api.add_resource(Campus, '/campuses/<int:id>')
api.add_resource(CampusList, '/campuses')
api.add_resource(Department,
                 '/departments/<int:id>',
                 '/campuses/<int:campus_id>/departments/<int:id>')
api.add_resource(DepartmentList,
                 '/departments',
                 '/campuses/<int:campus_id>/departments')
