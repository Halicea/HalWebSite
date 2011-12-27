from google.appengine.ext import db
import models.BaseModels as base

def clearDatastore():
    db.delete(base.Person.all())
    db.delete(base.Role.all())
    db.delete(base.WishList.all())
    db.delete(base.Invitation.all())
def importTestData():
    pass
