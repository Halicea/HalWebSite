from os import path
import os
import lib.paths as paths
import conf.settings as settings
from conf.imports import template
from lib.halicea.Magic import MagicSet
from lib.halicea import  mobile_agents
from lib.halicea.helpers import\
  DynamicParameters, LazyDict, ContentTypes, NotSuportedException
from lib.halicea.helpers import ClassImport
import simplejson

class HalBaseHandler(object):  
  def __init__(self, *args, **kwargs):
    self.params = None
    self.operations = {}
    #setattr(self.operations, 'update', self.upd)
    self.TemplateDir = settings.PAGE_VIEWS_DIR
    self.TemplateType = ''
    self.status = None
    self.isAjax=False
    self.responseType = 'html'
    self.requestType='html'
    
    if kwargs and kwargs.has_key('op'):
      self.op =kwargs['op']
    else:
      self.op = None
    self.method = 'GET'
    self.__templateIsSet__= False
    self.__template__ =""
    self.extra_context ={}
    self.dispatcher = HalActionDispatcher()
  
  def initialize( self, request, response):
    self.setup(request, response)
    #set the operations
    self.SetDefaultOperations()
    self.SetOperations()
    #set the plugins
    self.SetDefaultPlugins()
    self.SetPlugins()
        
  @classmethod
  def new_factory(cls, *args, **kwargs):
    """Create new request handler factory.
    
    Use factory method to create reusable request handlers that just
    require a few configuration parameters to construct.  Also useful
    for injecting shared state between multiple request handler
    instances without relying on global variables.  For example, to
    create a set of post handlers that will do simple text transformations
    you can write:
    
      class ChangeTextHandler(webapp.RequestHandler):
    
      def __init__(self, transform):
        self.transform = transform
      def post(self):
        response_text = self.transform(
          self.request.request.body_file.getvalue())
        self.response.out.write(response_text)
    
      application = webapp.WSGIApplication(
        [('/to_lower', ChangeTextHandler.new_factory(str.lower)),
         ('/to_upper', ChangeTextHandler.new_factory(str.upper)),
        ],
        debug=True)
    
    Text POSTed to /to_lower will be lower cased.
    Text POSTed to /to_upper will be upper cased.
    """
    def new_instance():
      return cls(*args, **kwargs)
    new_instance.__name__ = cls.__name__ #+ 'Factory'
    #setattr(new_instance, 'get_url', cls.get_url)
    return new_instance
 
  @classmethod
  def extend(cls, *args):
    cls.__bases__+=tuple([ClassImport(x) for x in args])
  
  def __get_template(self):
    if not self.__templateIsSet__:
      self.SetTemplate()
    return self.__template__
  Template =property(__get_template)
  def SetTemplate(self,templatePath=None):
    self.TemplateType = os.path.basename(settings.PAGE_VIEWS_DIR)
    self.TemplateDir, bn = MagicSet.baseName(self, True)
    name = bn+(self.op and '_'+self.op or '')+settings.VIEW_EXTENSTION
    if templatePath:
        res = templatePath.split('/')
        x = len(res)        
        if x>3:
          self.TemplateType = res[0]
          self.TemplateDir = '/'.join(res[1:-1])
          name = res[-1]
        elif x==3:
          self.TemplateType, self.TemplateDir, name = tuple(res)
        elif x==2:
          self.TemplateDir, name = tuple(res)
        elif x==1:
          name = res[0]
          
    self.__template__ = os.path.join(settings.VIEWS_DIR, self.TemplateType, self.TemplateDir, name)
    self.__templateIsSet__ = True
    

  def SetDefaultPlugins(self):
    if hasattr(settings, 'PLUGINS'):
      self.plugins = DynamicParameters(LazyDict(settings.PLUGINS, 'initialize', self.request, self.response))
  def SetPlugins(self):
    """This method needs to be overwritten in order to customize the plugins in the handler"""
    pass
  def SetDefaultOperations(self):
    if hasattr(settings, 'DEFAULT_OPERATIONS'):
      if settings.DEFAULT_OPERATIONS:
        self.operations.update(settings.DEFAULT_OPERATIONS)
        for k, v in self.operations.iteritems():
          if isinstance(v['method'], str):
            try:
              attr = getattr(self, v['method'])
              self.operations[k]={'method':attr}
            except Exception, ex:
              pass
          else:
            try:
              attr = getattr(self, v['method'].__name__)
              self.operations[k]={'method':attr}
            except Exception, ex:
              pass
  def SetOperations(self):
    """This method needs to be overwritten in order to customize the operations in the handler"""
    pass
   
  # Methods
  
#   the method by the operation
  def __route__(self, method, *args, **kwargs):
    """main in-class routing function
       in future it can be replaced with different routing methods
       now it routes in the methods by a given parameter named op
    """
    result = self.dispatcher.dispatch(self, *args, **kwargs)
    if result:
      self.respond(result)
      
  #otherwise we have been redirected
  def get(self, *args):
    return self.__route__('GET', *args)
  
  def post(self, *args):
    return self.__route__('POST', *args)
  
  def put(self, *args):
    return self.__route__('PUT', *args)
  
  def delete(self, *args, **kwargs):
    return self.__route__('DELETE', *args)
  
  def respond( self, item={}, *args ):
    #self.response.out.write(self.Template+'<br/>'+ dict)
    if self.responseType in ['html', 'xml', 'atom', 'rss']:
      if isinstance(item, dict):
        self.do_respond( template.render( self.Template, self.get_response_dict( item ),
                            debug = settings.TEMPLATE_DEBUG ))
      elif isinstance(item, str):
        self.do_respond(item)
      else:
        raise NotSuportedException("Only dictionary and string objects are accepted as return types from actions, insteat that an %s type is returned"%str(type(item)))        
    elif self.responseType =='json':
      self.do_respond(simplejson.dumps(item))
    else:#self.respond('text'):
      self.do_respond(item)
    
  def respond_static(self, text):
    self.do_respond(text)
    
  def redirect( self, uri, postargs={}, permanent=False ):
    innerdict = dict( postargs )
    if innerdict.has_key( 'status' ):
      self.status = innerdict['status']
      del innerdict['status']
    if self.status and self.session:
      self.session['status']=self.status
    if uri=='/Login' and not self.request.url.endswith('/Logout'):
      innerdict['redirect_url']=self.request.url
    if innerdict and len( innerdict ) > 0:
      params= '&'.join( [k + '=' + str(innerdict[k]) for k in innerdict] )
      if uri.find('?')==-1:
        return self.do_redirect(uri + '?' + params )
      elif uri.endswith('&'):
        return self.do_redirect( uri + params )
      else:
        return self.do_redirect( uri+ '&' + params )
    else:
      return self.do_redirect( uri )
    
  def redirect_login( self ):
    self.redirect( '/Login' )
  
  def get_response_dict(self, basedict ):
    result={}
    result.update(self.extra_context)
    result.update(basedict)

    if result.has_key( 'self' ):
      result.pop( 'self' )
    if not result.has_key('uri'):
      result['uri']=self.request.url
    if not result.has_key( 'status' ):
      result['status'] = self.status
    if not result.has_key('current_user'):
      result['current_user'] = self.User
    if not result.has_key('current_server'):
      result['current_server']=os.environ['HTTP_HOST']
    if not result.has_key('op'):
      result['op'] = self.op
    if not result.has_key('request'):
      result['this']=self
      
    #update the template paths
    #bases
    result.update(paths.GetBasesDict())
    #blocks
    result.update(paths.GetBlocksDict())
    #forms
    result.update(paths.GetFormsDict(path.join(settings.FORM_VIEWS_DIR, self.TemplateType))) ##end
    #current template directory
    result.update(paths.getViewsDict(os.path.dirname(self.Template)))
    
    if mobile_agents.detect_mobile(self.request): #decide if the request is mobile
      self.mobile = True
      result['mobile']='mobile'
      result['base']=os.path.join(os.path.dirname(result['base']), 'base_mobile.html')
    else:
      self.mobile = False
    return result
  
  def respondWith(self, responseType):
    """responseType can be ['json', 'html', 'xml', 'text']]"""
    if ContentTypes.has_key(responseType):
      self.responseType = responseType
      self.response.headers['Content-Type'] = ContentTypes[responseType] 
      
  def setup(self, request, response):
    raise NotImplementedError()
  
  def do_respond(self, text):
    raise NotImplementedError()
  
  def do_redirect(self, uri, permanent=True):
    raise NotImplementedError()
  
class HalActionDispatcher(object):
  def dispatch(self, controller, *args, **kwargs):
    
    action_func = controller.operations[controller.op or 'default']['method']
    if isinstance(action_func, str):
      if '.' in action_func:
        action_func = ClassImport(action_func)
      else:
        action_func = getattr(controller, action_func)
      if not action_func:
        raise Exception("Invalid action")
    elif not callable(action_func):
      raise NotSuportedException("Only string and callabels are accepted as Controller action arguments. Instead %s found."%str(type(action_func)))

    return action_func(controller, *args, **kwargs)


  