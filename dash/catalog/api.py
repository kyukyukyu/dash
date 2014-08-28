# -*- coding: utf-8 -*-
from flask import Blueprint, render_template
from flask.ext.login import login_required

from dash.extensions import api_manager
from dash.catalog.models import Campus, Department

campus_blueprint = api_manager.create_api_blueprint(
    Campus,
    methods=['GET'],
    )

department_blueprint = api_manager.create_api_blueprint(
    Department,
    methods=['GET'],
    )
