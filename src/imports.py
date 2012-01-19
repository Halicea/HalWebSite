# -*- coding: utf-8 -*-
"""This module is intended to be called only in the handler scripts(usualy located in the Apps directory)"""
from lib.halicea.templateEngines import appengineDjango as template
from lib.halicea.HalRequestHandler import HalRequestHandler
from google.appengine.ext.webapp.util import run_wsgi_app
from lib.gaesessions import SessionMiddleware
from conf.settings import EXTENSIONS, COOKIE_KEY

#register Extensions
HalRequestHandler.extend(*EXTENSIONS)
#end


def webapp_add_wsgi_middleware(app):
    app = SessionMiddleware(app, cookie_key=COOKIE_KEY)
    return app

def runapp(application):
    run_wsgi_app(webapp_add_wsgi_middleware(application))
