# -*- coding: utf-8 -*-
'''Helper utilities and decorators.'''
from flask import flash
import datetime
from dateutil.tz import tzutc


def flash_errors(form, category="warning"):
    '''Flash all errors for a form.'''
    for field, errors in form.errors.items():
        for error in errors:
            flash("{0} - {1}"
                  .format(getattr(form, field).label.text, error), category)

def utcnow():
    """Create :class:`datetime.datetime` object with UTC tzinfo."""
    return datetime.datetime.utcnow().replace(tzinfo=tzutc())
