# -*- coding: utf-8 -*-
"""This module is intended to be called only in the handler scripts(usualy located in the Apps directory)"""
from lib.halicea.templateEngines import appengineDjango as template
from lib.halicea.HalRequestHandler import HalRequestHandler as controller
from lib.routes.middleware import RoutesMiddleware
from lib.routes.mapper import Mapper
from lib.gaesessions import SessionMiddleware
from conf.settings import EXTENSIONS, COOKIE_KEY
from conf.settings import CONTROLLERS_DIR
from conf.settings import DEBUG
from lib.halicea.routes_helpers import get_controllers
from lib.halicea.wsgi import WSGIApplication
#register Extensions
controller.extend(*EXTENSIONS)
#end
def app_base(mapper, controllers_dict, debug):
  app = RoutesMiddleware(
            SessionMiddleware(
                WSGIApplication(controllers_dict, debug), 
                cookie_key=COOKIE_KEY
            ), 
            mapper, singleton=False)
  return app

def make_map(map_func, controllers, debug):
  """Create, configure and return the routes Mapper"""
  map = Mapper(controllers, always_scan=debug)
  map.minimization = False
  map_func(map)
  return map
  