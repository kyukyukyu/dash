# -*- coding: utf-8 -*-
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
import sqlalchemy.event
from dash.database import (
    Column,
    db,
    Model,
    ReferenceCol,
    relationship,
    SurrogatePK,
    UTCDateTime,
)
from dash.utils import utcnow


class CreatedAtMixin(object):

    """A mixin that adds a column named ``created_at`` which represents when
    the object was created in the application database.
    """

    created_at = Column(UTCDateTime(timezone=True),
                        nullable=False,
                        default=utcnow,
                        )


class CatalogEntity(SurrogatePK, Model, CreatedAtMixin):

    """An abstract class for catalog entities. The objects of subclasses of
    this class have column named ``code`` which identifies the objects in the
    source database, and column named ``created_at`` which represents when the
    object was created in the application database.
    """

    __abstract__ = True
    code = Column(db.String(40), unique=False, nullable=False)


class Campus(CatalogEntity):
    name = Column(db.String(80), unique=False, nullable=False)
    #: Module path for scraper script.
    scraper = Column(db.String(255), unique=True, nullable=False)
    __tablename__ = 'campuses'

    def __repr__(self):
        return u'<Campus({name})>'.format(name=self.name)


class DepartmentCourse(db.Model):
    """Association object class between Department and Course object.
    """
    __tablename__ = 'department_course'
    department_id = Column(db.Integer, db.ForeignKey('departments.id'), primary_key=True)
    course_id = Column(db.Integer, db.ForeignKey('courses.id'), primary_key=True)
    department = relationship('Department',
                              backref=db.backref('department_courses',
                                                 cascade='all, delete-orphan',
                                                 collection_class=set))
    course = relationship('Course',
                          backref=db.backref('department_courses',
                                             collection_class=set))

    def __init__(self, obj=None, department=None, course=None):
        """Initializer defined explicitly in order to make mock factory
        work correctly.

        :param obj: Parameter used in mock factory.
        :param department: Department object used in relationship.
        :param course: Course object used in relationship.
        """

        if obj is None:
            if department is None or course is None:
                raise ValueError('both department and course should be passed '
                                 'if obj is None')
            self.department = department
            self.course = course
        else:
            if isinstance(obj, Department):
                self.department = obj
            elif isinstance(obj, Course):
                self.course = obj
            else:
                raise TypeError('obj should be either Course or Department '
                                'type')


class Department(CatalogEntity):
    name = Column(db.String(80), unique=False, nullable=False)
    __tablename__ = 'departments'
    campus_id = ReferenceCol('campuses')
    campus = relationship('Campus', backref='departments')
    courses = association_proxy('department_courses', 'course')

    def __repr__(self):
        return u'<Department({name})>'.format(name=self.name)


class Subject(CatalogEntity):
    name = Column(db.String(80), unique=False, nullable=False)
    __tablename__ = 'subjects'

    def __repr__(self):
        return u'<Subject({name})>'.format(name=self.name)


class Course(CatalogEntity):
    __tablename__ = 'courses'
    __table_args__ = (
        db.CheckConstraint('target_grade IS NULL OR target_grade >= 0',
                           name='ck_courses_target_grade'),
    )
    instructor = Column(db.String(80), nullable=True)
    credit = Column(db.Float,
                    db.CheckConstraint('credit >= 0.0',
                                       name='ck_courses_credit',
                                       ),
                    nullable=False,
                    )
    subject_id = ReferenceCol('subjects')
    subject = relationship('Subject',
                           backref=db.backref('courses', lazy='dynamic'),
                           lazy='joined',
                           innerjoin=True,
                           )
    departments = association_proxy('department_courses', 'department')
    gen_edu_category_id = ReferenceCol('gen_edu_categories', nullable=True)
    gen_edu_category = relationship('GenEduCategory',
                                    backref=db.backref('courses',
                                                       lazy='dynamic'),
                                    lazy='joined',
                                    )
    target_grade = Column(db.Integer, nullable=True)
    #: True if a course might be said to be major.
    major = Column(db.Boolean, nullable=False)

    @hybrid_property
    def name(self):
        return self.subject.name

    @name.expression
    def name(self):
        return Subject.name

    @hybrid_property
    def subject_code(self):
        return self.subject.code

    @subject_code.expression
    def subject_code(self):
        return Subject.code

    @hybrid_property
    def general(self):
        """True if a course is associated with a general education
        category.
        """
        return self.gen_edu_category_id is not None

    @general.expression
    def general(self):
        return self.gen_edu_category_id.isnot(None)

    def __repr__(self):
        return '<Course({code})>'.format(code=self.code)


@sqlalchemy.event.listens_for(Course, 'before_insert')
@sqlalchemy.event.listens_for(Course, 'before_update')
def check_course(mapper, connection, course):
    """Checks the constraint about course type.
    """
    assert course.major is True or course.gen_edu_category_id is not None, \
        ('a course should be major or associated with a general '
         'education category')


class GenEduCategory(CatalogEntity):
    name = Column(db.String(80), unique=False, nullable=False)
    __tablename__ = 'gen_edu_categories'

    def __repr__(self):
        return u'<GenEduCategory({name})>'.format(name=self.name)


class CourseClass(SurrogatePK, Model, CreatedAtMixin):
    __tablename__ = 'course_classes'
    day_of_week = Column(db.Integer, nullable=False)
    start_period = Column(db.Integer, nullable=False)
    end_period = Column(db.Integer, nullable=False)
    course_id = ReferenceCol('courses')
    course = relationship(
        'Course',
        backref=db.backref(
            'classes',
            order_by='CourseClass.day_of_week, CourseClass.start_period',
            lazy='joined',
        ),
        )

    __table_args__ = (
        db.CheckConstraint('day_of_week >= 0 AND day_of_week < 7',
                           name='ck_course_classes_day_of_week'),
        db.CheckConstraint('start_period >= 0 AND end_period >= 0 AND '
                           'start_period <= end_period',
                           name='ck_course_classes_start_end_period'),
    )

    def conflicts_with(self, h):
        if not isinstance(h, CourseClass):
            raise TypeError('h should be a CourseClass object')

        return (
            self.day_of_week == h.day_of_week and (
                self.start_period <= h.end_period and
                self.end_period >= h.start_period
            )
        )

    def __repr__(self):
        return '<CourseClass({day_of_week}, {start_period}, {end_period})>' \
            .format(day_of_week=self.day_of_week,
                    start_period=self.start_period,
                    end_period=self.end_period,
                    )
