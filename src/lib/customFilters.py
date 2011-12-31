from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
register = webapp.template.create_template_register()
from django.template import resolve_variable, Node, TemplateSyntaxError, VariableDoesNotExist
# access a dictionary
def hash(h, key):
    return h[key] 
register.filter(hash)

class CallNode(Node):
    def __init__(self, object, method, args=None, kwargs=None, context_name=None):
        self.object = object
        self.method = method
        if args:
            self.args = []
            for arg in args:
                self.args.append(arg)
        else:
            self.args = None

        if kwargs:
            self.kwargs = {}
            for key in kwargs:
                self.kwargs[key] = kwargs[key]
        else:
            self.kwargs = None

        self.context_name = context_name

    def render(self, context):
        object = resolve_variable(self.object, context)
        if isinstance(object, str):
            raise TemplateSyntaxError('Given object is string ("%s") of length %d' 
                                               % (object, len(object)))

        args = []
        kwargs = {}
        if self.args:
            for arg in self.args:
                args.append(resolve_variable(arg, context))
        if self.kwargs:
            for key in self.kwargs:
                kwargs[key] = resolve_variable(self.kwargs[key],context)

        method = getattr(object, self.method, None)

        if method:
            if hasattr(method, '__call__'): 
                result = method(*args, **kwargs)
            else:
                result = method
            if self.context_name:
                context[self.context_name] = result
                return ''
            else:
                if not result == None: 
                    return result
                else:
                    return ''
        else:
            raise TemplateSyntaxError('Model %s doesn\'t have method "%s"' 
                                               % (object._meta.object_name, self.method))

@register.tag
def call(parser, token):
    """
    Passes given arguments to given method and returns result

    Syntax::

        {% call <object>[.<foreignobject>].<method or attribute> [with <*args> <**kwargs>] [as <context_name>] %}

    Example usage::

        {% call article.__unicode__ %}
        {% call article.get_absolute_url as article_url %}
        {% call article.is_visible with user %}
        {% call article.get_related with tag 5 as related_articles %}

        {% call object.foreign_object.test with other_object "some text" 123 article=article text="some text" number=123 as test %} 
    """

    bits = token.split_contents()
    syntax_message = ("%(tag_name)s expects a syntax of %(tag_name)s "
                       "<object>.<method or attribute> [with <*args> <**kwargs>] [as <context_name>]" %
                       dict(tag_name=bits[0]))

    temp = bits[1].split('.')
    method = temp[-1]
    object = '.'.join(temp[:-1])

    # Must have at least 2 bits in the tag
    if len(bits) > 2:
        try:
            as_pos = bits.index('as')
        except ValueError:
            as_pos = None
        try:
            with_pos = bits.index('with')
        except ValueError:
            with_pos = None

        if as_pos:
            context_name = bits[as_pos+1]
        else:
            context_name = None

        if with_pos:
            if as_pos:
                bargs = bits[with_pos+1:as_pos]
            else:
                bargs = bits[with_pos+1:]
        else:
            bargs = []

        args = []
        kwargs = {}

        if bargs:
            for barg in bargs:
                t = barg.split('=')
                if len(t) > 1:
                    kwargs[t[0]] = t[1]
                else:
                    args.append(t[0])

        return CallNode(object, method, args=args, kwargs=kwargs, context_name=context_name)
    elif len(bits) == 2:
        return CallNode(object, method)
    else:
        raise TemplateSyntaxError(syntax_message)