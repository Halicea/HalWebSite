from lib.halicea.HalBaseHandler import HalBaseHandler
from lib.halicea.helpers import DynamicParameters, RequestDictMixin, ContentTypes, ContentTypes_reverse
from google.appengine.ext import webapp
import simplejson

class HalRequestHandler(HalBaseHandler, webapp.RequestHandler):
    """Base Request handler class for the Hal framework.
        Note: standard items that are responded in the context are:
           - {{current_user}}
           - {{status}} - returning the self.status variable (also stored in session and useful for redirects)
           - {{current_server}} -responding the server url
           - {{current_url}}
           - {{this}}
    """
    def __init__(self, *args, **kwargs):
        super(HalRequestHandler, self).__init__(*args, **kwargs)
    
    def setup(self, request, response):
        """Initializes this request handler with the given Request and Response.
           Set the Default Plugins and Handlers
            and Apply any customizations if defined
        """
        self.request = request
        self.response = response
        
        if ContentTypes_reverse.has_key(self.request.headers.environ.get('CONTENT_TYPE')):
            self.requestType =ContentTypes_reverse[self.request.headers.environ.get('CONTENT_TYPE')]
        else:
            self.requestType = ContentTypes['html']
            
        if self.requestType =='json':
            data = simplejson.loads(self.request.body)
            self.params = DynamicParameters(data)
#        elif self.requestType=='xml':
#            data = serializers.deserialize('xml', self.request.body)
#            #TODO handle the parameters
#            self.params = DynamicParameters(RequestDictMixin(self.request))
        else:
            self.params = DynamicParameters(RequestDictMixin(self.request))
        self.method = self.request.environ['REQUEST_METHOD']
        
        self.isAjax = ((request.headers.environ.get('HTTP_X_REQUESTED_WITH')=='XMLHttpRequest') or (request.headers.get('X-Requested-With')=='XMLHttpRequest'))
        if not self.isAjax: self.isAjax = self.params.isAjax=='true'
        if self.session:
            if self.session.has_key( 'status' ): self.status = self.session.pop('status')

    def do_respond(self, text):
        self.response.out.write(text)
        
    def do_redirect(self, uri, *args):
        webapp.RequestHandler.redirect(self, uri, *args)
    