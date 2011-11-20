from google.appengine.ext import db
from lib.halicea.decorators import *
from Magic import MagicSet
@View(templateGroup='page', templateType='Shared', templateName='edit.html')
def edit(request, *args, **kwargs):
    if request.params.key:
        item = db.get(request.params.key)
        if item:
            return {'op':'upd', 'form': MagicSet.getFormClass(request)(instance=item)}
        else:
            request.status = 'Item does not exists'
            request.redirect(request.get_url())
    else:
        request.status = 'Key not provided'
        return {'op':'ins' ,'form':MagicSet.getFormClass(request)()}

@View(templateGroup='page', templateType='Shared', templateName='index.html')
def index(request, *args, **kwargs):
    results =None
    result = {'items': MagicSet.getModelClass(request).all().fetch(limit=1000)}
    return result.update(locals())

@View(templateGroup='page', templateType='Shared', templateName='details.html')
def details(request, *args, **kwargs):
     if request.params.key:
        return {'item':db.get(request.params.key)}
     else:
         request.status='Not Valid key was provided'

def delete(request, *args, **kwargs):
    if request.params.key:
        item = db.get(request.params.key)
        if item:
            item.delete()
            request.status = 'Item is Deleted'
        else:
            request.status = 'Item does not exist'
    else:
        request.status = 'Key was not provided'
    request.redirect(request.get_url())

def save(request, *args, **kwargs):
    if request.params.key:
        item = db.get(request.params.key)
    form = MagicSet.getFormClass(request)(data=request.POST, instance=item)
    if form.is_valid():
        result=form.save(commit=False)
        result.put()
        request.status = 'Item is saved'
    else:
        request.status = 'Form is not Valid'
    request.redirect(request.get_url())
