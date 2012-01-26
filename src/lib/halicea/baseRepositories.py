from google.appengine.ext import db
class GaeRepo(object):
  t=None
  save = lambda *args: db.put(*args)
  delete = lambda *args:db.delete(*args)
  all = lambda t:db.all(t)