from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect, Http404
from lib.halicea.HalRequestHandler import HalRequestHandler
class DjangoRequestHandler(HalRequestHandler):
    def __init__(self, *args, **kwargs):
        super(DjangoRequestHandler, self).__init__(*args, **kwargs)

    def __call__(self, request,*args, **kwargs):
        request = request
        response = HttpResponse()
        setattr(response, 'headers', response._headers)
        self.initialize(request, response )
        if self.request.method =='POST':
            return self.post()
        if self.request.method =='GET':
            return self.get()
        return None
    def __respond(self, text):
        self.response.content = text
        return self.response

    def __redirect(self, uri, *args):
        return HttpResponseRedirect(uri, *args)
