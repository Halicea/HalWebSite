'''
Created on 04.1.2010

@author: KMihajlov
'''
#from lib import messages
from conf.settings import DEBUG
from lib import messages
from lib.halicea import ContentTypes as ct
import traceback,logging
#from Controllers.MyRequestHandler import MyRequestHandler as mrh
import warnings
def property(function):
    keys = 'fget', 'fset', 'fdel'
    func_locals = {'doc':function.__doc__}
    def probe_func(frame, event, arg):
        if event == 'return':
            locals = frame.f_locals
            func_locals.update(dict((k, locals.get(k)) for k in keys))
#            sys.settrace(None)
        return probe_func
#    sys.settrace(probe_func)
    function()
    return property(**func_locals)

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
        self.default =method

    def __call__(self, f):
        def new_f(request, *args, **kwargs):
            request.operations['default']={'method':self.default}
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
    def __init__(self, **template):
        self.template = template
    def __call__(self, f):
        def new_f(request, *args, **kwargs):
            request.SetTemplate(**self.template)
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
    def __init__(self, redirect_url='/Login', message= messages.must_be_loged):
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
    def __init__(self, redirect_url='/Login', message= messages.must_be_admin):
        self.redirect_url = redirect_url
        self.message = message
        self.handler = None

    def __call__(self, f):
        def new_f(request, *args, **kwargs):
            if request.User and request.User.IsAdmin:
                return f(request, *args, **kwargs)
            else:
                request.status= self.message
                request.redirect(self.redirect_url)
        CopyDecoratorProperties(f, new_f)
        return new_f
class InRole(object):
    def __init__(self, role='Admin',redirect_url='/Login', message= messages.must_be_in_role):
        self.redirect_url = redirect_url
        self.message = message
        self.handler = None

    def __call__(self, f):
        def new_f(request, *args, **kwargs):
            if request.User and request.User.IsAdmin:
                return f(request, *args, **kwargs)
            else:
                request.status= self.message
                request.redirect(self.redirect_url)
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
                if request.response.headers['Content-Type']== ct.JSON:
                    if self.showStackTrace:
                        return '''{message:"%s", stackTrace:"%s"}'''%(str(ex)+'\n'+traceback.format_exc())
                    else:
                        return '''{message:%s}'''%(self.message)
                elif request.response.headers['Content-Type']== ct.XML:
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
        """context_docts is an array of dictionaries or a single dictionary"""
        if isinstance(context_dicts, dict):
            self.context_dicts = [context_dicts,]
        elif isinstance(context_dicts, list):
            self.context_dicts = context_dicts
        else:
            raise Exception("Wrong Extra context input variable, Mut be either dict of list of dicts")

    def __call__(self, f):
        def new_f(request, *args, **kwargs):
            if self.context_dicts:
                for d in self.context_dicts:
                    request.extra_context.update(d)
            return f(request, *args, **kwargs)
        CopyDecoratorProperties(f, new_f)
        return new_f
# End Decorators for handler Methods