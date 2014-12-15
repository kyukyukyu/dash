# -*- coding: utf-8 -*-
from flask import Blueprint, render_template
from collections import Mapping
from six import add_metaclass, iteritems
from flask.views import MethodViewType
from flask.ext.login import login_required
from flask.ext.restful import (
    Resource,
    reqparse,
    fields,
    marshal,
)

from dash.catalog import models
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


class Entity(Resource):
    model = None
    fields = None

    @classmethod
    def query(cls, **kwargs):
        return cls.model.query

    def get(self, **kwargs):
        id = kwargs['id']
        entity = self.query(**kwargs).filter_by(id=id).one()
        return marshal(entity, self.fields), 200


class Collection(Resource):
    model = None
    fields = None

    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int)
    parser.add_argument('results_per_page', type=int)

    @classmethod
    def query(cls, **kwargs):
        return cls.model.query

    def get(self, **kwargs):
        args = self.parser.parse_args()
        page = args.get('page') or 1

        query = self.query(**kwargs)
        pagination = query.paginate(
            page,
            per_page=args.get('results_per_page') or 20,
        )

        ret_objects = marshal(pagination.items, self.fields)
        return {
            'num_results': pagination.total,
            'page': page,
            'num_pages': pagination.pages,
            'objects': ret_objects,
        }, 200


class Campus(Entity):
    model = models.Campus
    fields = campus_fields


class CampusList(Collection):
    model = models.Campus
    fields = campus_fields


class Department(Entity):
    model = models.Department
    fields = department_fields


class DepartmentList(Collection):
    model = models.Department
    fields = department_fields


class ResourceUnderResource(MethodViewType):
    def __new__(mcs, clsname, bases, dct):
        new_dct = dict(dct)
        parent_column_name = new_dct.pop('parent_column_name')

        @classmethod
        def query(cls, **kwargs):
            q = super(cls, cls).query(**kwargs)
            parent_id = kwargs[parent_column_name]
            parent_column = getattr(cls.model, parent_column_name)
            return q.filter(parent_column == parent_id)

        new_dct['query'] = query

        return super(ResourceUnderResource, mcs).__new__(mcs, clsname, bases,
                                                         new_dct)


@add_metaclass(ResourceUnderResource)
class CampusDepartment(Department):
    parent_column_name = 'campus_id'


@add_metaclass(ResourceUnderResource)
class CampusDepartmentList(DepartmentList):
    parent_column_name = 'campus_id'


class Subject(Entity):
    model = models.Subject
    fields = subject_fields


class SubjectList(Collection):
    model = models.Subject
    fields = subject_fields


api.add_resource(Campus, '/campuses/<int:id>')
api.add_resource(CampusList, '/campuses')
api.add_resource(Department, '/departments/<int:id>')
api.add_resource(DepartmentList, '/departments')
api.add_resource(CampusDepartment, '/campuses/<int:campus_id>'
                                   '/departments/<int:id>')
api.add_resource(CampusDepartmentList, '/campuses/<int:campus_id>'
                                       '/departments')
