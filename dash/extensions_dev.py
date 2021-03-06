# -*- coding: utf-8 -*-
"""Extensions module for development environment. Each extension is
initialized in the app factory located in app.py
"""

from flask.ext.debugtoolbar import DebugToolbarExtension
debug_toolbar = DebugToolbarExtension()
