from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect, Http404
from lib.halicea.HalRequestHandler import HalBaseHandler
from lib.halicea.helpers import DynamicParameters, RequestDictMixin, ContentTypes, ContentTypes_reverse
import simplejson

class DjangoRequestHandler(HalBaseHandler):
  def __init__(self, *args, **kwargs):
    super(DjangoRequestHandler, self).__init__(*args, **kwargs)
   
  def __call__(self, request,*args, **kwargs):
    self.request = request
    self.response = HttpResponse()
    setattr(self.response, 'headers', self.response._headers)
    self.initialize(self.request, self.response)
    
  def do_respond(self, text):
    self.response.content = text
    return self.response

  def do_redirect(self, uri, *args):
    return HttpResponseRedirect(uri, *args)
  
  def setup(self, request, response):
    """Initializes this request handler with the given Request and Response.
       Set the Default Plugins and Handlers
      and Apply any customizations if defined
    """
    self.request = request
    self.response = response
    #TODO: finish this part with the dynamic dict
    
    if ContentTypes_reverse.has_key(self.request.headers.environ.get('CONTENT_TYPE')):
      self.requestType =ContentTypes_reverse[self.request.headers.environ.get('CONTENT_TYPE')]
    else:
      self.requestType = ContentTypes['html']
      
    if self.requestType =='json':
      data = simplejson.loads(self.request.body)
      self.params = DynamicParameters(data)
#    elif self.requestType=='xml':
#      data = serializers.deserialize('xml', self.request.body)
#      #TODO handle the parameters
#      self.params = DynamicParameters(RequestDictMixin(self.request))
    else:
      self.params = DynamicParameters(RequestDictMixin(self.request))
    self.method = self.request.environ['REQUEST_METHOD']
    
    self.isAjax = ((request.headers.environ.get('HTTP_X_REQUESTED_WITH')=='XMLHttpRequest') or (request.headers.get('X-Requested-With')=='XMLHttpRequest'))
    if not self.isAjax: self.isAjax = self.params.isAjax=='true'
    if self.session:
      if self.session.has_key( 'status' ): self.status = self.session.pop('status')
