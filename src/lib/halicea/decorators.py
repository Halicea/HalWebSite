'''
Created on 04.1.2010

@author: KMihajlov
'''
#from lib import messages
from conf.settings import DEBUG
from lib import messages
import traceback,logging
from lib.halicea import cache
import warnings
from lib.halicea.helpers import ClassImport, NotSuportedException,\
  NotAllowedError


def CopyDecoratorProperties(func, new_func):
  new_func.__name__ = func.__name__
  new_func.__doc__ = func.__doc__
  new_func.__dict__.update(func.__dict__)

def deprecated(func):
  """This is a decorator which can be used to mark functions
  as deprecated. It will result in a warning being emitted
  when the function is used."""
  def new_func(*args, **kwargs):
    warnings.warn("Call to deprecated function %s." % func.__name__,
            category=DeprecationWarning)
    return func(*args, **kwargs)
  CopyDecoratorProperties(func, new_func)
  return new_func

#Decorators for Set Operations Method

class ClearDefaults(object):
  def __init__(self):
    pass
  def __call__(self, f):
    def new_f(request, *args, **kwargs):
      request.operations ={}
      return f(request, *args, **kwargs)
    CopyDecoratorProperties(f, new_f)
    return new_f

class Post(object):
  def __init__(self):
    pass
  def __call__(self, f):
    def new_f(request, *args, **kwargs):
      if request.method!='POST':
        raise Exception('Only Post requests are accepted from the handler')
      return f(request, *args, **kwargs)
    CopyDecoratorProperties(f, new_f)
    return new_f

class Get(object):
  def __call__(self, f):
    def new_f(request, *args, **kwargs):
      if request.method!='GET':
        raise Exception('Only GET requests are accepted from the handler')
      return f(request, *args, **kwargs)
    CopyDecoratorProperties(f, new_f)
    return new_f

def Put(func):
  def new_f(request, *args, **kwargs):
    if request.method!='PUT':
      raise Exception('Only PUT requests are accepted from the handler')
    return func(request, *args, **kwargs)
  return new_f

class Methods(object):
  def __init__(self, *args):
    self.methods = args
  def __call__(self, f):
    def new_f(request, *args, **kwargs):
      if not request.method in self.methods:
        raise Exception('Only '+str(self.methods)+' are allowed. Request was made with '+request.method)
      return f(request, *args, **kwargs)
    CopyDecoratorProperties(f, new_f)
    return new_f

class Default(object):
  def __init__(self, method):
    self.default = method
    if isinstance(self.default, str):
      self.key=method
    elif callable(method):
      self.key = method.__name__
    else:
      raise NotSuportedException('Only callables and strings are accepted as arguments, instead %s was given'%str(type(self.default)))

  def __call__(self, f):
    def new_f(request, *args, **kwargs):
      request.operations['default']={'method':self.default}
      request.operations[self.key]={'method':self.default}      
      result = f(request, *args, **kwargs)
      return result
    CopyDecoratorProperties(f, new_f)
    return new_f

class Handler(object):
  def __init__(self, operation=None, method=None):
    self.operation = operation or 'default'
    if method:
      self.method = method
    else:
      self.method = operation
  def __call__(self, f):
    def new_f(request, *args, **kwargs):
      if self.operation:
        request.operations[self.operation] ={'method':self.method}
      return f(request, *args, **kwargs)
    CopyDecoratorProperties(f, new_f)
    return  new_f
#End Decorators for Set Operations Method

# Decorators for Handler Methods

class View(object):
  def __init__(self, template):
    self.template = template
    
  def __call__(self, f):
    def new_f(request, *args, **kwargs):
      if callable(self.template):
        request.SetTemplate(self.template(request, *args, **kwargs))
      else:
        request.SetTemplate(self.template)
      return f(request, *args, **kwargs)
    CopyDecoratorProperties(f, new_f)
    return new_f

class ResponseHeaders(object):
  def __init__(self, **kwargs):
    self.d =kwargs
  def __call__(self, f):
    def new_f(request, *args, **kwargs):
      for k, v in self.d.iteritems():
        request.response.headers[k]=v
      return f(request, *args, **kwargs)
    CopyDecoratorProperties(f, new_f)
    return new_f

class LogInRequired(object):
  def __init__(self, redirect_url='/login', message= messages.must_be_loged):
    self.redirect_url = redirect_url
    self.message = message
    self.handler = None

  def __call__(self, f):
    def new_f(request, *args, **kwargs):
      if request.User:
        return f(request, *args, **kwargs)
      else:
        request.redirect(self.redirect_url)
        request.status= self.message
    CopyDecoratorProperties(f, new_f)
    return new_f

class AdminOnly(object):

  def __init__(self, redirect_url='/login', message= messages.must_be_admin):
    self.redirect_url = redirect_url
    self.message = message
    self.handler = None

  def __call__(self, f):
    def new_f(request, *args, **kwargs):
      if request.User and request.User.IsAdmin:
        return f(request, *args, **kwargs)
      elif self.redirect_url:
        request.status= self.message
        request.redirect(self.redirect_url)
      else:
        raise NotAllowedError("Access is Not Allowed")
      
    CopyDecoratorProperties(f, new_f)
    return new_f
  
class InRole(object):
  def __init__(self, role='Admin',redirect_url='/login', message= messages.must_be_in_role):
    self.redirect_url = redirect_url
    self.message = message
    self.handler = None

  def __call__(self, f):
    def new_f(request, *args, **kwargs):
      if request.User and request.User.IsAdmin:
        return f(request, *args, **kwargs)
      elif self.redirect_url:
        request.status= self.message
        request.redirect(self.redirect_url)
      else:
        raise NotAllowedError("Access is Not Allowed")
    CopyDecoratorProperties(f, new_f)
    return new_f
  
class ErrorSafe(object):
  def __init__(self,
         redirectUrl = '/',
         message= messages.error_happened,
         Exception = Exception,
         showStackTrace = False ):
    self.redirectUrl = redirectUrl
    self.message = message
    self.Exception = Exception
    self.showStackTrace = showStackTrace
  def __call__(self, f):
    def new_f(request, *args, **kwargs):
      try:
        return f(request, *args, **kwargs)
      except self.Exception, ex:
        if request.ResponseType == 'json':
          if self.showStackTrace:
            return '''{message:"%s", stackTrace:"%s"}'''%(str(ex)+'\n'+traceback.format_exc())
          else:
            return '''{message:%s}'''%(self.message)
        elif request.ResponseType == 'xml':
          if self.showStackTrace:
            return '''<root><message>%s</message><stackTrace>%s</stackTrace></root>"'''%(str(ex)+'\n'+traceback.format_exc())
          else:
            return '''<root><message>%s</message></root>'''%(self.message)
        else:
          if request.status == None:
            request.status = self.message or ''
          else:
            request.status += self.message or ''
          logging.error(str(ex)+'\n'+traceback.format_exc())
          if self.showStackTrace or DEBUG:
            request.status+= "  Details:<br/>"+ex.__str__()+'</br>'+traceback.format_exc()
          else:
            'There has been some problem, and the moderator was informed about it.'
          request.redirect(self.redirectUrl)
    CopyDecoratorProperties(f, new_f)
    return new_f

class ExtraContext(object):
  def __init__(self, context_dicts):
    """context_dicts is an array of dictionaries or a single dictionary"""
    if isinstance(context_dicts, dict):
      self.context_dicts = [context_dicts,]
    elif isinstance(context_dicts, list):
      self.context_dicts = context_dicts
    else:
      raise Exception("Wrong ExtraContext constructor variable, Must be either dictionary of list of dictionaries")

  def __call__(self, f):
    def new_f(request, *args, **kwargs):
      if self.context_dicts:
        for d in self.context_dicts:
          request.extra_context.update(d)
      return f(request, *args, **kwargs)
    CopyDecoratorProperties(f, new_f)
    return new_f
# End Decorators for handler Methods

#Cache Decorators

class Cached(object):
  @staticmethod
  def resName(res , request, *args, **kwargs):
    #fully identify the source by it's name and parameters
    return '__RESOURCE__'+request.__module__+"."+request.__name__+'.'+res.__name__+\
            '('+\
              ','.join(set([\
                ','.join([str(x) for x in args]),\
                ','.join([x+'='+str(kwargs[x]) for x in kwargs.iterkeys()])
              ]))+\
            ')'
  @staticmethod
  def clear(action, *args, **kwargs):
    cache.delete(Cached.resName(action, action.im_class, *args, **kwargs))
    
  def __init__(self, time=0, namespace=None, condition=None):
    self.namespace=namespace
    self.time=time
    self.condition = condition
  def __call__(self, f):
    
    def new_f(request, *args, **kwargs):
      if not DEBUG and (not self.condition or self.condition(request, *args, **kwargs)):
        resName = Cached.resName(f, request.__class__,*args, **kwargs)
        res = cache.get(resName)
        if not res:
          res = f(request, *args, **kwargs)
          cache.set(resName, res, self.time, namespace=self.namespace)
        return res
      else:
        return f(request, *args, **kwargs)
    CopyDecoratorProperties(f, new_f)
    return new_f

class ClearCacheAfter(object):
  """Clears the cache of a given controller action after the execution of the called action
    Example:
      
      @ClearCacheAfter(SomeControllerClass.Method, *methodargs, **methodskwargs)
      def delete(self, arguments)
  """
  def __init__(self, action, params_function=None):
    if params_function:
      self.params_f = params_function
    else:
      self.params_f = lambda r, *args, **kwargs: ((),{})
    if isinstance(action, str):
      a = action.split('.')
      klass = ClassImport('.'.join(a[:-1]))
      self.action = getattr(klass, a[-1])
    else:
      self.action = action
  def __call__(self, f):
    def new_f(request, *args, **kwargs):
      res = f(request, *args, **kwargs)
      args_p, kwargs_p = self.params_f(request, *args, **kwargs)
      Cached.clear(self.action, *args_p, **kwargs_p)
      return res
    CopyDecoratorProperties(f, new_f)
    return new_f
  
class ClearCacheFirst(object):
  """Clears the cache of a given controller action before the execution of the called action
    Example:
      
      @ClearCacheFirst(SomeControllerClass.Method, *methodargs, **methodskwargs)
      def delete(self, arguments)
  """
  def __init__(self, action, params_function=None):
    if params_function:
      self.params_f = params_function
    else:
      self.params_f = lambda r, *args, **kwargs: ((),{})
    self.action = action
  def __call__(self, f):
    def new_f(request, *args, **kwargs):
      args_p, kwargs_p = self.params_function(request, *args, **kwargs)
      Cached.clear(self.action, *args_p, **kwargs_p)
      return f(request, *args, **kwargs)
    CopyDecoratorProperties(f, new_f)
    return new_f  
# 

class ResponseType():
  """sets the response type of the controller action""" 
  def __init__(self, contentType):
    if isinstance(contentType, str):
      self.responseType = lambda request, *args, **kwargs: contentType
    else:
      self.responseType = contentType
  def __call__(self, f):
    def new_f(request, *args, **kwargs):
      request.ResponseType = self.responseType(request, *args, **kwargs)
      return f(request, *args, **kwargs)
    CopyDecoratorProperties(f, new_f)
    return new_f
    