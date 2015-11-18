# -*- coding: utf-8 -*-
from contextlib import contextmanager
import collections

from dash.extensions import db


__all__ = ['update_catalog']


@contextmanager
def update_catalog(campus):
    """Context manager for updating catalog of a campus with entities
    from data source.

    This returns an object with interface that can be used for adding
    multiple types of entities from data source. These are the types:

    * :py:class:`Department` entities
    * :py:class:`Subject` entities
    * :py:class:`GenEduCategory` entities
    * :py:class:`Course` entities

    There are relationships between entity types. Here is the
    relationships:

    * :py:class:`Department` (many-to-many) :py:class:`Course`. A
    course may be related with no department entities.
    * :py:class:`Subject` (one-to-many) :py:class:`Course`
    * :py:class:`GenEduCategory` (one-to-many) :py:class:`MajorCourse`

    For these kinds of relationships, relationships should be defined
    by setting the value of relationship field to related object when
    passed to this context manager. For example, let ``s`` be a
    :py:class:`Subject` object, and ``c`` be a :py:class:`Course`
    object. ``s`` and ``c`` are supposed to be related. When ``c`` is
    passed to this context manager using provided interfaces,
    ``c.subject`` should have been set to ``s``.

    When exited, this sends database some queries to get stored
    entities and relationships, then proceeds with one-way sync from
    data source to database.

    One-way sync is done with set operations on codes of entities.
    Let A be the set of codes of entities from data source, and B be
    the set of codes of entities from database. Entities whose code is
    a member of (B - A) are to be deleted from database. Entities whose
    code is a member of (A ∩ B) are to be updated in database. Entities
    whose code is a member of (A - B) are to be created in database.
    Sync for entities can be done in this order:

    1. Delete {e | code(e) ∈ B - A} from database.
    2. For each entity in A, check if the entity with same code exists
    in database. If exists, update it. If not, create it.

    Syncing relationships is similar to syncing entities. Relationships
    are usually derived from filtering results of data source. For
    example, the relationships between department entities and course
    entities can be derived by searching courses by departments in
    course registration system. If department 'Major in Computer
    Science' is selected for filtering, courses in the search result
    should be associated with the department.

    :param campus: Campus of which catalog will be updated.
    :type campus: :py:class:`dash.catalog.models.Campus`
    """
    catalog = Catalog()
    yield catalog
    for d in catalog.departments:
        d.campus = campus
    db.session.add_all(catalog.departments)
    db.session.add_all(catalog.subjects)
    db.session.add_all(catalog.gen_edu_categories)
    db.session.add_all(catalog.courses)
    db.session.commit()


class Catalog(object):
    """Catalog class whose object will be returned by context manager.

    User of context manager calls functions in this class to add entity
    objects to be synced. On calling such functions, passed entity
    objects are held by object of this class. These objects will be
    used in context manager to run one-way sync from data source to
    database.
    """

    def __init__(self):
        self.departments = []
        self.subjects = []
        self.gen_edu_categories = []
        self.courses = []

    def hold_departments(self, departments):
        """Holds a set of department objects.

        :param departments: Set of department objects.
        :type departments: :py:class:`collections.Iterable`
        """
        self.departments.extend(departments)

    def hold_subjects(self, subjects):
        """Holds a set of subject objects.

        :param subjects: Set of subject objects.
        :type subjects: :py:class:`collections.Iterable`
        """
        self.subjects.extend(subjects)

    def hold_gen_edu_categories(self, categories):
        """Holds a set of general education category objects.

        :param categories: Set of general education category objects.
        :type categories: :py:class:`collections.Iterable`
        """
        self.gen_edu_categories.extend(categories)

    def hold_courses(self, courses):
        """Holds a set of course objects.

        :param courses: Set of course objects.
        :type courses: :py:class:`collections.Iterable`
        """
        self.courses.extend(courses)
