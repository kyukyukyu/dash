# -*- coding: utf-8 -*-
import datetime as dt

from dash.database import (
    Column,
    db,
    Model,
    ReferenceCol,
    relationship,
    SurrogatePK,
)


class CodeMixin(object):

    """A mixin that adds a column named ``code`` which identifies the objects
    of specific class in the source database.
    """

    code = Column(db.String(40), nullable=False)


class CreatedAtMixin(object):

    """A mixin that adds a column named ``created_at`` which represents when
    the object was created in the application database.
    """

    created_at = Column(db.DateTime,
                        nullable=False,
                        default=dt.datetime.utcnow
                        )


class CatalogEntity(SurrogatePK, Model, CreatedAtMixin):

    """An abstract class for catalog entities. The objects of subclasses of
    this class have column named ``code`` which identifies the objects in the
    source database, column named ``name`` which represents the name of each
    object, and column named ``created_at`` which represents when the object
    was created in the application database.
    """

    __abstract__ = True
    code = Column(db.String(40), unique=False, nullable=False)
    name = Column(db.String(80), unique=False, nullable=False)


class Campus(CatalogEntity):
    __tablename__ = 'campuses'

    def __repr__(self):
        return '<Campus({name})>'.format(name=self.name)


class Department(CatalogEntity):
    __tablename__ = 'departments'
    campus_id = ReferenceCol('campuses')
    campus = relationship('Campus', backref='departments')

    def __repr__(self):
        return '<Department({name})>'.format(name=self.name)


class Course(CatalogEntity):
    __tablename__ = 'courses'

    def __repr__(self):
        return '<Course({name})>'.format(name=self.name)


class Lecture(CatalogEntity):
    __tablename__ = 'lectures'
    __table_args__ = (
        db.CheckConstraint('credit >= 0.0', name='ck_lectures_credit'),
        db.CheckConstraint('target_grade IS NULL OR target_grade >= 0',
                           name='ck_lectures_target_grade',
                           ),
    )
    instructor = Column(db.String(80), nullable=True)
    credit = Column(db.Float, nullable=False)
    target_grade = Column(db.Integer, nullable=True)
    course_id = ReferenceCol('courses')
    course = relationship('Course',
                          backref=db.backref('lectures', lazy='dynamic'),
                          )
    department_id = ReferenceCol('departments', nullable=True)
    department = relationship('Department', backref='lectures')
    campus = relationship('Campus',
                          uselist=False,
                          secondary=Department.__table__,
                          backref=db.backref('lectures', lazy='dynamic'),
                          )

    def __repr__(self):
        return '<Department({name})>'.format(name=self.name)


class LectureHour(SurrogatePK, Model, CreatedAtMixin):
    __tablename__ = 'lecture_hours'
    __table_args__ = (
        db.CheckConstraint('day_of_week >= 0 AND day_of_week < 7',
                           name='ck_lecture_hours_day_of_week'),
        db.CheckConstraint('start_time >= 0 AND end_time >= 0 AND '
                           'start_time <= end_time',
                           name='ck_lecture_hours_start_end_time'),
    )
    day_of_week = Column(db.Integer, nullable=False)
    start_time = Column(db.Integer, nullable=False)
    end_time = Column(db.Integer, nullable=False)
    lecture_id = ReferenceCol('lectures')
    lecture = relationship(
        'Lecture',
        backref=db.backref(
            'hours',
            order_by='LectureHour.day_of_week, LectureHour.start_time',
        ),
        )

    def conflicts_with(self, h):
        if not isinstance(h, LectureHour):
            raise TypeError('h should be a LectureHour object')

        return (
            self.day_of_week == h.day_of_week and (
                self.start_time <= h.end_time and
                self.end_time >= h.start_time
            )
        )

    def __repr__(self):
        return '<LectureHour({day_of_week}, {start_time}, {end_time})>' \
            .format(day_of_week=self.day_of_week,
                    start_time=self.start_time,
                    end_time=self.end_time,
                    )
