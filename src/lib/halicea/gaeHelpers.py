import datetime
"""
Helpers for appengine hosted application
"""
import time
from google.appengine.ext import db

SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)
class ModelToDict(object):
    """Callable to convert an appengine Model to a Dictionary that can be 
       then easy represented with Json or Xml
    """
    def __call__(self, model):
        output = {}
        for key, prop in model.properties().iteritems():
            value = getattr(model, key)
    
            if value is None or isinstance(value, SIMPLE_TYPES):
                output[key] = value
            elif isinstance(value, datetime.date):
                # Convert date/datetime to ms-since-epoch ("new Date()").
                ms = time.mktime(value.utctimetuple()) * 1000
                ms += getattr(value, 'microseconds', 0) / 1000
                output[key] = int(ms)
            elif isinstance(value, db.GeoPt):
                output[key] = {'lat': value.lat, 'lon': value.lon}
            elif isinstance(value, db.Model):
                output[key] = ModelToDict(value)
            else:
                raise ValueError('cannot encode ' + repr(prop))
        return output
    