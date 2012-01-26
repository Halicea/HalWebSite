# -*- coding: utf-8 -*-
from conf.imports import *
from conf.settings import DEBUG
from conf.settings import CONTROLLERS_DIR
from conf.handlerMap import webapphandlers
app = app_base(make_map(lambda handler_map:handler_map.extend(webapphandlers), 
                        get_controllers(CONTROLLERS_DIR).keys(), 
                        DEBUG),
               get_controllers(CONTROLLERS_DIR),  
               DEBUG)