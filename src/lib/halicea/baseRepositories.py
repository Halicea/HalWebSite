from google.appengine.ext import db
class GaeRepo(object):
    type=None
    save = lambda *args: db.put(*args)
    delete = lambda *args:db.delete(*args)
    all = lambda type:db.all(type)