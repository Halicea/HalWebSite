import conf.settings as settings
from imports import *
from google.appengine.ext import webapp
application = webapp.WSGIApplication(webapphandlers, debug=settings.DEBUG)
if __name__ == '__main__':
    runapp(application)