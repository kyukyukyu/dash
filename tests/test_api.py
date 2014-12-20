# -*- coding: utf-8 -*-
import collections
import pytest
import dateutil.parser
from six import text_type as unicode
from six.moves.urllib import parse
from .factories import DepartmentFactory
from functools import reduce
from dash.compat import UnicodeMixin


class Url(UnicodeMixin):

    def __init__(self, entity_name, entity_id=None, prefix=u""):
        self.entity_name = unicode(entity_name)
        self.entity_id = unicode(entity_id) if entity_id is not None else None
        self.path = list()
        self.prefix = unicode(prefix)
        self._query = dict()

    @classmethod
    def copy(cls, url_obj):
        if not isinstance(url_obj, Url):
            raise TypeError('url_obj should be an Url object')

        u = Url(unicode(url_obj.entity_name))
        entity_id = url_obj.entity_id
        u.entity_id = unicode(entity_id) if entity_id is not None else None
        u.path = list(url_obj.path)
        u.prefix = unicode(url_obj.prefix)
        u._query = dict(url_obj._query)

        return u

    def collection(self, entity_name):
        if self.entity_id is None:
            raise ValueError('cannot call collection() on the Url object '
                             'which has no entity_id')
        u = Url.copy(self)
        u.entity_name = entity_name
        u.entity_id = None
        u.path.append((self.entity_name, self.entity_id))
        return u

    def col(self, entity_name):
        return self.collection(entity_name)

    def entity(self, entity_id):
        if self.entity_id is not None:
            raise ValueError('cannot call entity() on the Url object '
                             'which has entity_id')
        u = Url.copy(self)
        u.entity_id = entity_id
        return u

    def ent(self, entity_id):
        return self.entity(entity_id)

    def query(self, mapping=None, **kwargs):
        _query_new = dict(self._query)

        if mapping is not None:
            if not isinstance(mapping, collections.Mapping):
                raise TypeError('mapping should be a mapping object')
            _query_new.update(mapping)
        _query_new.update(kwargs)

        u = Url.copy(self)
        u._query.update(_query_new)
        return u

    def __unicode__(self):
        def f(x, y):
            if y[1] is None:
                return x + u"/{}".format(y[0])
            else:
                return x + u"/{}/{}".format(*y)

        def it():
            for p in self.path:
                yield p

            yield (self.entity_name, self.entity_id)

        url = reduce(f, it(), self.prefix)
        if self._query:
            url = u"{}?{}".format(url, parse.urlencode(self._query))

        return url


class TestCatalogEntityApi(object):

    @classmethod
    def assert_response(self, resp):
        assert resp.status_code == 200
        assert resp.content_type == 'application/json'

    @classmethod
    def assert_entity(cls, entity, json):
        assert json['id'] == entity.id
        assert json['code'] == entity.code
        assert dateutil.parser.parse(json['created_at']) == \
               entity.created_at.replace(microsecond=0)


class TestCampusApi(TestCatalogEntityApi):

    base_url = Url('campuses', prefix="/api")   # "/api/campuses"

    @classmethod
    def assert_entity(cls, entity, json):
        super(TestCampusApi, cls).assert_entity(entity, json)
        assert json['name'] == entity.name
        map(TestDepartmentApi.assert_entity, entity.departments,
            json['departments'])

    def test_get_campus(self, campuses, testapp):
        campus = campuses[0]
        resp = testapp.get(self.base_url.entity(campus.id))
        self.assert_response(resp)

        self.assert_entity(campus, resp.json)

    def test_get_campuses(self, campuses, testapp):
        resp = testapp.get(self.base_url)
        self.assert_response(resp)

        campuses = sorted(campuses, key=lambda c: c.id)

        objects = resp.json['objects']
        assert len(objects) == \
            resp.json['num_results'] == \
            len(campuses)
        map(self.assert_entity, campuses, objects)

    def test_get_campus_department(self, db, campuses, testapp):
        campus = campuses[0]
        department = DepartmentFactory(campus=campus)
        db.session.commit()

        url = self.base_url \
                  .ent(campus.id) \
                  .col('departments') \
                  .ent(department.id)
        resp = testapp.get(url)
        self.assert_response(resp)

        TestDepartmentApi.assert_entity(department, resp.json)

    def test_get_campus_departments(self, db, campuses, testapp):
        campus = campuses[0]
        departments = [
            DepartmentFactory(campus=campus),
            DepartmentFactory(campus=campus),
            DepartmentFactory(campus=campus),
        ]
        db.session.commit()

        url = self.base_url \
                  .ent(campus.id) \
                  .col('departments')
        resp = testapp.get(url)
        self.assert_response(resp)

        departments = sorted(departments, key=lambda d: d.id)

        objects = resp.json['objects']
        assert len(objects) == \
            resp.json['num_results'] == \
            len(departments)
        map(TestDepartmentApi.assert_entity, departments, objects)


class TestDepartmentApi(TestCatalogEntityApi):

    base_url = Url('departments', prefix="/api")    # "/api/departments"

    @classmethod
    def assert_entity(cls, entity, json):
        super(TestDepartmentApi, cls).assert_entity(entity, json)
        assert json['name'] == entity.name
        assert json['campus_id'] == entity.campus_id

    def test_get_department(self, departments, testapp):
        department = departments[0]
        resp = testapp.get(self.base_url.entity(department.id))
        self.assert_response(resp)

        self.assert_entity(department, resp.json)

    def test_get_departments(self, departments, testapp):
        resp = testapp.get(self.base_url)
        self.assert_response(resp)

        departments = sorted(departments, key=lambda d: d.id)

        objects = resp.json['objects']
        assert len(objects) == resp.json['num_results'] == \
            len(departments)
        map(self.assert_entity, departments, objects)
