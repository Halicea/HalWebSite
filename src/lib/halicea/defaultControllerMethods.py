from google.appengine.ext import db
from lib.halicea.decorators import View, ResponseType
from Magic import MagicSet
from lib.halicea import ContentTypes
@View('shared/index.html')
@ResponseType(lambda r, *args,**kwargs:kwargs.has_key('type') and kwargs['type'] or 'html')
def index(request, *args, **kwargs):
  return {'items': MagicSet.getModelClass(request).all().fetch(limit=1000)}

@View('shared/view.html')
@ResponseType(lambda r, *args,**kwargs:kwargs.has_key('type') and kwargs['type'] or 'html')
def view(request, *args, **kwargs):
  if request.params.key:
    return {'item':db.get(request.params.key)}
  else:
    request.status='Not Valid key was provided'

@View('shared/edit.html')
@ResponseType(lambda r, *args,**kwargs:kwargs.has_key('type') and kwargs['type'] or 'html')  
def edit(request, *args, **kwargs):
  if request.params.key:
    item = db.get(request.params.key)
    if item:
      return {'op':'save', 'form': MagicSet.getFormClass(request)(instance=item)}
    else:
      request.status = 'Item does not exists'
      request.redirect(request.get_url())
  else:
    return {'op':'insert' ,'form':MagicSet.getFormClass(request)()}

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
