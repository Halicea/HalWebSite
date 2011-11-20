from google.appengine.ext import db
#{% block imports%}
#{%endblock%}
################
class Welcome(db.Model):
    """TODO: Describe Welcome"""
    
    @classmethod
    def CreateNew(cls  , _isAutoInsert=False):
        result = cls()
        if _isAutoInsert: result.put()
        return result
    def __str__(self):
        #TODO: Change the method to represent something meaningful
        return 'Change __str__ method' 
## End Welcome
