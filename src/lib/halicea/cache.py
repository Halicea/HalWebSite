from conf.settings import RUN

#Choose which cache to proxy 
if RUN =='appengine':
    from google.appengine.api import memcache
else:
    from memcache import Client
    #TODO: get it from the settings module 
    memcache = Client('localhost',1120)

__cache__ = memcache
#proxy for caching
def get(key, default=None):
    return __cache__.get(key) or default
def set(key, item, time=0, namespace=None):
    return __cache__.set(key, item, time=time, namespace=namespace)
def delete(key):
    return __cache__.delete(key)

