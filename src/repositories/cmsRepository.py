from google.appengine.ext import db
from models.cmsModels import *

def clearDatastore():
    db.delete(CMSContent.all())
    db.delete(CMSLink.all())
    db.delete(ContentTag.all())
    db.delete(Menu.all())
    
def importTestData():
    pass
    