# -*- coding: utf-8 -*-
from conf.imports import *
import conf.settings as settings
from conf.handlerMap import webapphandlers
from google.appengine.ext import webapp

application = webapp.WSGIApplication(webapphandlers, debug=settings.DEBUG)
if __name__ == "__main__":
    runapp(application)