# -*- coding: utf-8 -*-
from conf.imports import *
import conf.settings as settings
from conf.handlerMap import webapphandlers
from google.appengine.ext import we
import webapp2
application = webapp2.WSGIApplication(webapphandlers, debug=settings.DEBUG)
if __name__ == "__main__":
  runapp(application)