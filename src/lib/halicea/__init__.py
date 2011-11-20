# set models properties
"""from google.appengine.ext.db import Model
def cmp(self, other):
    if(not isinstance(other, Model)):
        return False
    else:
        return str(self.key()) == str(other.key())
#Easier comparison for models
setattr(Model, '__cmp__', cmp)
"""