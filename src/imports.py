# -*- coding: utf-8 -*-

"""This module is intended to be called on in the handler scripts(usualy located in the Apps directory)"""
import os
import re
os.environ['DJANGO_SETTINGS_MODULE']  = 'conf.settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
import google.appengine.ext.webapp.template
from django.conf import settings
settings._target=None
from handlerMap import webapphandlers
from google.appengine.ext.webapp.util import run_wsgi_app
from lib.gaesessions import SessionMiddleware
COOKIE_KEY = '''2zÆœ;¾±þ”¡j:ÁõkçŸÐ÷8{»Ën¿A—jÎžQAQqõ"bøó÷*%†™ù¹b¦$vš¡¾4ÇŸ^ñ5¦'''
def webapp_add_wsgi_middleware(app):
    from google.appengine.ext.appstats import recording
    app = SessionMiddleware(app, cookie_key=COOKIE_KEY)
    #app = recording.appstats_wsgi_middleware(app)
    return app
def runapp(application):
    run_wsgi_app(webapp_add_wsgi_middleware(application))
