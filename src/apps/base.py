# -*- coding: utf-8 -*-
from imports import *
import conf.settings as settings
from google.appengine.ext import webapp
from handlerMap import webapphandlers
application = webapp.WSGIApplication(webapphandlers, debug=settings.DEBUG)
if __name__ == "__main__":
    runapp(application)
