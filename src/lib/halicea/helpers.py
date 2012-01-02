from UserDict import DictMixin

class NotSuportedException(Exception):
    def __init__(self, message):
        self.message = message or "Operation is not supported"
    def __str__(self):
        return self.message

def ClassImport(name):
    components = name.split('.')
    mod = __import__('.'.join(components[:-1]), fromlist=[components[-1]])
    klass = getattr(mod, components[-1])
    return klass

class DynamicParameters(object):
    dictObject = None
    def __init__(self, dictObject={}, default=None):
        self.dictObject = dictObject
        self.defaultValue= default
    def __getattr__(self, name):
        if self.dictObject.has_key(name):
            return self.dictObject[name]
        else:
            return self.default
    def __setattr__(self, name, value):
        if(name!='dictObject' and name!='defaultValue'):
            self.dictObject[name] = value
        else:
            self.__dict__[name]=value
    def get(self, name , default=None):
        if self.dictObject.has_key(name):
            return self.dictObject[name]
        else:
            return default

class RequestDictMixin(DictMixin):
    def __init__(self, request):
        self.request = request
    def __getitem__(self, key):
        return self.request.get(key)
    def __setitem__(self, key, item):
        raise NotSuportedException("Request parameters are read only")
    def __delitem__(self, key):
        raise NotSuportedException("Request parameters are read only")
    def keys(self):
        pass

class LazyDict(DictMixin): 
    def __init__(self, types, init_method, *args, **kwargs):
        self.objects = {}
        self.init_method = ''
        self.args = args
        self.kwargs = kwargs
        for k in types:
            self.objects[k[0]] = [ClassImport(k[1]), None]
    def __getitem__(self, key):
        if not self.objects[key]:
            raise Exception("Invalid Property "+key)
        elif not self.objects[key][1]:
            self.objects[key][1] = self.objects[key][0]()
            if hasattr(self.objects[key][1],  self.init_method):
                getattr(self.objects[key][1], self.init_method)(self.objects[key][1], *self.args, **self.kwargs)
        return self.objects[key][1]
    def __setitem__(self, key, item):
        self.objects[key] = (item.__class__, item)
    def __delitem__(self, key):
        del self.objects[key]
    def keys(self):
        return self.objects.keys()
