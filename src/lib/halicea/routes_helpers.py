'''
Created on Jan 21, 2012

@author: costa
'''
import os
import inspect
from conf.settings import CONTROLLER_CLASS_SUFIX
from conf.settings import CONTROLLER_EXTENSTION
from conf.settings import CONTROLLER_MODULE_SUFIX
from conf.settings import PROJ_LOC
def get_controllers(directory):
  result = {}
  rootModule = os.path.relpath(directory, PROJ_LOC).replace(os.path.pathsep, '.')
  for root, dirs, files in os.walk(directory):
    pre = root[len(directory):]
    for f in files:     
      if f.endswith(CONTROLLER_MODULE_SUFIX+CONTROLLER_EXTENSTION):
        info = inspect.getmoduleinfo(os.path.join(root, f))
        module = 'controllers'+'.'+info.name
        base = __import__(module, fromlist=['controllers'])
        for name in [x for x in dir(base) if x.endswith(CONTROLLER_CLASS_SUFIX)]:
          obj = getattr(base, name)
          if inspect.isclass(obj):
            result[name[:-len(CONTROLLER_CLASS_SUFIX)].lower()]= module+'.'+name
  return result
