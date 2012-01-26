from os import path
import os
import lib.paths as paths
import conf.settings as settings
from conf.imports import template
from lib.halicea.Magic import MagicSet
from lib.halicea import  mobile_agents
from lib.halicea.helpers import DynamicParameters, LazyDict, ContentTypes
from lib.halicea.helpers import ClassImport
import simplejson
templateGroups = {'form':settings.FORM_VIEWS_DIR,
          'page':settings.PAGE_VIEWS_DIR,
          'block':settings.BLOCK_VIEWS_DIR,
          'base':settings.BASE_VIEWS_DIR,}

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
      self.SetTemplate(None, None, None)
    return self.__template__
  Template =property(__get_template)
  def SetTemplate(self,templateGroup=None, templateType=None, templateName=None):
    bn = MagicSet.baseName(self)
#    templateTypes = The specific modelFullName
    if not templateGroup:
      self.TemplateDir =settings.PAGE_VIEWS_DIR
    else:
      self.TemplateDir = templateGroups[templateGroup]

    if not templateType:
      self.TemplateType = bn[:bn.rindex('.')].replace('.', path.sep)
    else:
      self.TemplateType = templateType.replace('.', path.sep)

    if not templateName: #default name will be set
      self.__template__ = os.path.join(self.TemplateDir, self.TemplateType, bn[bn.rindex('.')+1:])
      if self.op:
        self.__template__ += '_'+self.op
      self.__template__+=settings.VIEW_EXTENSTION
    else:
      self.__template__ = os.path.join(self.TemplateDir, self.TemplateType, templateName)
      
    self.__templateIsSet__ = True
    def GetTemplatePath(self, templateGroup=None, templateType=None, templateName=None):
      tDir = None
      tType =None

      result = None
      if templateName == templateGroup == templateType == None and self.__templateIsSet__:
        return self.Template
      bn = MagicSet.baseName(self)
      #templateTypes = The specific modelFullName
      if not templateGroup:
        tDir =settings.PAGE_VIEWS_DIR
      else:
        tDir = templateGroups[templateGroup]
  
      if not templateType:
        tType = bn[:bn.rindex('.')].replace('.', path.sep)
      else:
        tType = templateType.replace('.', path.sep)
  
      if not templateName: #default name will be set
        result = os.path.join(tDir, tType, bn[bn.rindex('.')+1:])
        if self.op:
          result += '_'+self.op
        else:
          try:
            result += '_'+self.operations['default']['method'].__name__
          except :
            result += '_'+self.operations['default']['method']
        result+=settings.VIEW_EXTENSTION
      else:
        result = os.path.join(tDir, tType, templateName)
      return result
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
    self.method = method
    #if there is explicitly setup opration then use that one
    if self.params.op:
      self.op= self.params.op
       
    outresult = 'No Result returned'
    if self.operations.has_key(self.op):
      if isinstance(self.operations[self.op]['method'], str):
        outresult = getattr(self, self.operations[self.op]['method'])(*args, **kwargs)
      else:
        if hasattr(self, self.operations[self.op]['method'].__name__):
          outresult = getattr(self, self.operations[self.op]['method'].__name__)(*args, **kwargs)
        else:
          outresult = self.operations[self.op]['method'](self, *args, **kwargs)
    else:
      if isinstance(self.operations['default']['method'], str):
        outresult = getattr(self, self.operations['default']['method'])(*args, **kwargs)
      else:
        if hasattr(self, self.operations['default']['method'].__name__):
          outresult = getattr(self, self.operations['default']['method'].__name__)(*args, **kwargs)
        else:
          outresult = self.operations['default']['method'](self, *args, **kwargs)
    if outresult!=None:
      return self.respond(outresult)
  
  #otherwise we have been redirected
  def get(self, *args):
    """Used to comply with the appengines webob Controller"""
    return self.__route__('GET', *args)
  def post(self, *args):
    """Used to comply with the appengines webob Controller"""
    return self.__route__('POST', *args)
  def put(self, *args):
    return self.__route__('PUT', *args)
  def respond( self, item={}, *args ):
    #self.response.out.write(self.Template+'<br/>'+ dict)
    if self.responseType =='html':
      if isinstance(item, dict):
        self.do_respond( template.render( self.Template, self.get_response_dict( item ),
                            debug = settings.TEMPLATE_DEBUG ))
      elif isinstance(item,list):
        return self.do_respond('<ul>'+'\n'.join(['<li>'+str(x)+'</li>' for x in item])+'</ul>')
      else:
        self.do_respond(str(item))        
    elif self.responseType =='json':
      self.do_respond(simplejson.dumps(item))
    else:#self.responseType('text'):
      self.do_respond(str(item))
        
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
    #update the variables
    result.update(paths.GetBasesDict())
    result.update(paths.GetBlocksDict())
    result.update(paths.GetFormsDict(path.join(settings.FORM_VIEWS_DIR, self.TemplateType))) ##end
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