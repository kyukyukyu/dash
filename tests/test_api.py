# -*- coding: utf-8 -*-
import collections
import itertools
import pytest
import dateutil.parser
from six import text_type as unicode
from six.moves.urllib import parse
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

    def append(self, child_url):
        if self.entity_id is None:
            raise ValueError('cannot call append() on the Url object '
                             'which has no entity_id')
        u = Url.copy(self)
        for entity_name, entity_id in child_url.path:
            u = u.collection(entity_name).entity(entity_id)
        u = u.collection(child_url.entity_name).entity(child_url.entity_id)
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
    def assert_response(cls, resp):
        assert resp.status_code == 200
        assert resp.content_type == 'application/json'

    @classmethod
    def assert_entity(cls, entity, json):
        assert json['id'] == entity.id
        assert json['code'] == entity.code
        assert dateutil.parser.parse(json['created_at']) == \
               entity.created_at.replace(microsecond=0)

    @classmethod
    def entity_test_under_campuses(cls, campuses, entity, testapp,
                                   url_processors=[]):
        for campus in itertools.chain([None], campuses):
            should_exist = True
            if campus:
                url = TestCampusApi.base_url.ent(campus.id) \
                    .append(cls.base_url).ent(entity.id)
                if entity.campus is not campus:
                    should_exist = False
            else:
                url = cls.base_url.ent(entity.id)

            for processor in url_processors:
                url = processor(url)

            if should_exist:
                resp = testapp.get(url)
                cls.assert_response(resp)
                cls.assert_entity(entity, resp.json)
            else:
                resp = testapp.get(url, status=404)

    @classmethod
    def collection_test_under_campuses(cls, campuses, collection, testapp,
                                       url_processors=[]):
        collection = sorted(collection, key=lambda o: o.id)
        for campus in itertools.chain([None], campuses):
            if campus:
                url = TestCampusApi.base_url.ent(campus.id) \
                    .append(cls.base_url)
                expected_objs = [o for o in collection if o.campus == campus]
            else:
                url = cls.base_url
                expected_objs = list(collection)

            for processor in url_processors:
                url = processor(url)

            resp = testapp.get(url)
            cls.assert_response(resp)

            result_objs = resp.json['objects']
            assert len(result_objs) == resp.json['num_results'] == \
                len(expected_objs)
            map(cls.assert_entity, expected_objs, result_objs)


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


class TestDepartmentApi(TestCatalogEntityApi):

    base_url = Url('departments', prefix="/api")    # "/api/departments"

    @classmethod
    def assert_entity(cls, entity, json):
        super(TestDepartmentApi, cls).assert_entity(entity, json)
        assert json['name'] == entity.name
        assert json['campus_id'] == entity.campus_id

    def test_get_department(self, campuses, departments, testapp):
        department = departments[0]
        self.entity_test_under_campuses(campuses, department, testapp)

    def test_get_departments(self, campuses, departments, testapp):
        self.collection_test_under_campuses(campuses, departments, testapp)
