# -*- coding: utf-8 -*-
import collections
import itertools
import pytest
import dateutil.parser
from six import text_type as unicode
from six.moves.urllib import parse
from functools import reduce
from dash.compat import UnicodeMixin
from dash.catalog.models import GeneralCourse, MajorCourse
from .factories import MajorCourseFactory


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

    @staticmethod
    def entity_test_under_campus(entity, campus):
        return entity.campus is campus

    @classmethod
    def entity_test_under_campuses(cls, campuses, entity, testapp,
                                   url_processors=[]):
        for campus in itertools.chain([None], campuses):
            should_exist = True
            if campus:
                url = TestCampusApi.base_url.ent(campus.id) \
                    .append(cls.base_url).ent(entity.id)
                if not cls.entity_test_under_campus(entity, campus):
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
                expected_objs = [o for o in collection
                                 if cls.entity_test_under_campus(o, campus)]
            else:
                url = cls.base_url
                expected_objs = list(collection)

            for processor in url_processors:
                url = processor(url)

            resp = testapp.get(url)
            cls.assert_response(resp)

            num_results = resp.json['num_results']
            assert num_results == len(expected_objs)

            p = 1
            pos = 0
            while pos < num_results:
                url_paged = url.query(page=p)
                resp = testapp.get(url_paged)
                cls.assert_response(resp)

                result_objs = resp.json['objects']
                map(cls.assert_entity, expected_objs[pos:(pos + 20)],
                    result_objs)
                p += 1
                pos += 20


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


class TestSubjectApi(TestCatalogEntityApi):
    base_url = Url('subjects', prefix="/api")   # "/api/subjects"

    @classmethod
    def assert_entity(cls, entity, json):
        super(TestSubjectApi, cls).assert_entity(entity, json)
        assert json['name'] == entity.name

    def test_get_subject(self, subjects, testapp):
        subject = subjects[0]
        resp = testapp.get(self.base_url.entity(subject.id))
        self.assert_response(resp)

        self.assert_entity(subject, resp.json)

    def test_get_subjects(self, subjects, testapp):
        resp = testapp.get(self.base_url)
        self.assert_response(resp)

        subjects = sorted(subjects, key=lambda s: s.id)

        objects = resp.json['objects']
        assert len(objects) == resp.json['num_results'] == \
            len(subjects)
        map(self.assert_entity, subjects, objects)


class TestGenEduCategoryApi(TestCatalogEntityApi):

    base_url = Url('gen_edu_categories', prefix="/api")

    @classmethod
    def assert_entity(cls, entity, json):
        super(TestGenEduCategoryApi, cls).assert_entity(entity, json)
        assert json['name'] == entity.name

    def test_get_category(self, gen_edu_categories, testapp):
        category = gen_edu_categories[0]
        resp = testapp.get(self.base_url.ent(category.id))
        self.assert_response(resp)

        self.assert_entity(category, resp.json)

    def test_get_categories(self, gen_edu_categories, testapp):
        resp = testapp.get(self.base_url)
        self.assert_response(resp)

        gen_edu_categories = sorted(gen_edu_categories, key=lambda c: c.id)

        objects = resp.json['objects']
        assert len(objects) == resp.json['num_results'] == \
               len(gen_edu_categories)
        map(self.assert_entity, gen_edu_categories, objects)


class TestCourseApi(TestCatalogEntityApi):

    base_url = Url('courses', prefix="/api")   # "/api/courses"

    @classmethod
    def assert_entity(cls, entity, json):
        super(TestCourseApi, cls).assert_entity(entity, json)
        assert json['instructor'] == entity.instructor
        assert json['credit'] == entity.credit
        assert json['subject_id'] == entity.subject_id
        TestSubjectApi.assert_entity(entity.subject, json['subject'])
        for expected_dept, result_dept in zip(entity.departments, json['departments']):
            TestDepartmentApi.assert_entity(expected_dept, result_dept)
        for expected_class, result_class in zip(entity.classes, json['classes']):
            assert result_class['id'] == expected_class.id
            assert result_class['day_of_week'] == expected_class.day_of_week
            assert result_class['start_period'] == expected_class.start_period
            assert result_class['end_period'] == expected_class.end_period

        assert json['type'] == entity.type
        if isinstance(entity, GeneralCourse):
            assert json['category_id'] == entity.category_id
            TestGenEduCategoryApi.assert_entity(entity.category,
                                                json['category'])
        elif isinstance(entity, MajorCourse):
            assert json['target_grade'] == entity.target_grade

    @staticmethod
    def entity_test_under_campus(entity, campus):
        return any(map(lambda d: d.campus_id == campus.id,
                       entity.departments))

    def test_get_course(self, campuses, courses, testapp):
        course = courses[0]
        self.entity_test_under_campuses(campuses, course, testapp)

    def test_get_courses(self, campuses, courses, testapp):
        self.collection_test_under_campuses(campuses, courses, testapp)

    def test_paging_get_courses(self, campuses, departments, db, testapp):
        courses = []
        n_deps = len(departments)
        for i in range(100):
            c = MajorCourseFactory(departments=[departments[i % n_deps]])
            courses.append(c)
        db.session.commit()
        self.collection_test_under_campuses(campuses, courses, testapp)

    def test_get_courses_open_for_multiple_dept(self, campuses, departments,
                                                db, testapp):
        courses = []
        for i in range(100 // len(departments)):
            c = MajorCourseFactory(departments=departments)
            courses.append(c)
        db.session.commit()
        self.collection_test_under_campuses(campuses, courses, testapp)

    @pytest.mark.parametrize("name,codes_from_name", [
        ("understanding",
         frozenset(["10037", "15254", "15002", "11543", "11970", "22294",
                    "22361", "20025"])),
        (None, None),
    ])
    @pytest.mark.parametrize("subject_code,codes_from_subject_code", [
        ("GEN6006", frozenset(["10037", "15254"])),
        (None, None),
    ])
    @pytest.mark.parametrize("instructor,codes_from_instructor", [
        ("Sunny Yoon", frozenset(["15254", "11552", "12798"])),
        (None, None),
    ])
    @pytest.mark.parametrize("course_type,category_id,target_grade,"
                             "department_id,codes_from_options", [
        ("general", 1, None, None, frozenset(["15254"])),
        ("general", None, None, None, frozenset(["15254", "15002", "20025",
                                                 "20016"])),
        ("major", None, 3, 1, frozenset(["10037"])),
        ("major", None, 3, None, frozenset(["10037", "11552", "11543",
                                            "22294", "22291"])),
        ("major", None, None, 1, frozenset(["10037", "11615"])),
        ("major", None, None, None, frozenset(["10037", "11615", "11552",
                                               "11543", "12798", "11970",
                                               "22294", "22361", "22291"])),
        (None, None, None, None, None),
    ])
    def test_search_courses(
            self, campuses, courses, testapp,
            name, codes_from_name,
            subject_code, codes_from_subject_code,
            instructor, codes_from_instructor,
            course_type, category_id, target_grade,
            department_id, codes_from_options,
    ):
        selected_course_codes_all = set(c.code for c in courses)
        for code_set in (codes_from_name, codes_from_subject_code,
                         codes_from_instructor, codes_from_options):
            if code_set is None:
                continue
            selected_course_codes_all = selected_course_codes_all & code_set
        selected_courses_all = list(c for c in courses
                                    if c.code in selected_course_codes_all)

        def process_search_options(url):
            if name:
                url = url.query(name=name)
            if subject_code:
                url = url.query(subject_code=subject_code)
            if instructor:
                url = url.query(instructor=instructor)
            if course_type:
                url = url.query({'type': course_type})
            if category_id:
                url = url.query(category_id=category_id)
            if target_grade:
                url = url.query(target_grade=target_grade)
            if department_id:
                url = url.query(department_id=department_id)

            return url

        self.collection_test_under_campuses(
            campuses, selected_courses_all, testapp,
            url_processors=[process_search_options],
            )
