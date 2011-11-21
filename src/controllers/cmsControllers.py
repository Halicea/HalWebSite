import yaml
from lib.halicea.decorators import *
import models.cmsModels as cms
from controllers.BaseControllers import LoginController
from lib.halicea.HalRequestHandler import HalRequestHandler as hrh
from forms.cmsForms import CMSContentForm
from google.appengine.ext import db
from lib import messages
from django.utils import simplejson

class CMSBaseController(hrh):
    def __init__(self, *args, **kwargs):
        super(CMSBaseController, self).__init__(*args, **kwargs)
        self.extra_context={'tags':cms.ContentTag.all().order('-Count').fetch(10, 0)}

class CMSLinksController(CMSBaseController):
    def __init__(self, *args, **kwargs):
        super(CMSLinksController, self).__init__(*args, **kwargs)
    @Handler(method='save', operation='save')
    @Handler('LinksTree')
    def SetOperations(self):pass
    @AdminOnly()
    @View(templateName='CMSLinks.html')
    def index(self, menu='cms',*args):
        limit = 100
        offset = 0
        try:
            offset = int(self.params.offset)
        except:
            pass
        resultMenu = cms.Menu.get_by_key_name(menu)
        if not resultMenu:
            root = cms.CMSLink.get_or_insert(
                         key_name = menu, 
                         AddressName=menu, Name=menu, 
                         Creator=self.User, ContentTypeNumber=2)
            resultMenu = cms.Menu.CreateFromLinkRoot(menu, 'None', None, root, True) 
        contents = cms.CMSContent.all().order('-DateCreated').fetch(limit=limit, offset=offset)
        return {'menu':resultMenu, 'contents':contents}
    @AdminOnly()
    def save(self, *args):
        addressName = self.params.addressName
        name=self.params.name
        parent=self.params.parentLink
        if parent:
            parent = cms.CMSLink.get(parent)
        else:
            parent = None
        order= int(self.g('order'))
        content=self.params.content or None
        contentType = cms.ContentType.StaticPage
        if content:
            content = cms.CMSContent.get(content)
            contentType=cms.ContentType.CMSPage
        if not self.params.HasContent:
            contentType = cms.ContentType.NoContent
        creator= self.User
        if True: #TODO: validation
            cms.CMSLink.CreateNew2(addressName, name, parent, order, content, contentType, creator, _isAutoInsert=True)
        
        if self.isAjax:
            return self.LinksTree(self.params.menu)
        else:
            return self.index()
    @AdminOnly()
    def delete(self, *args):
        lnk=cms.CMSLink.get(self.params.key)
        if lnk:
            if lnk.Content and lnk.Content.content_cms_links.count()==1:
                lnk.Content.delete()
            lnk.delete()
            self.status='Link is deleted'
        else:
            self.status="Link is invalid";
        return self.isAjax and self.status or self.redirect(self.get_url())

    def LinksTree(self, menu):
        return cms.Menu.get_by_key_name(menu).to_list()
    
class MenuController(CMSBaseController):
    def __init__(self, *args, **kwargs):
        super(MenuController, self).__init__(*args, **kwargs)
    @ClearDefaults()
    @Default('view')
    def SetOperations(self):pass
    
    @CachedResource()
    def view(self, menu='cms'): 
        result=  cms.Menu.get_by_key_name(menu)
        if result:
            return result.to_list(self.params)
        else:
            return "No Menu Found"
    def index(self):
        return {'menus':cms.Menu.all()}
    
class CMSContentController(CMSBaseController):
    def __init__(self, *args, **kwargs):
        super(CMSContentController, self).__init__(*args, **kwargs)
        self.ContentForm = CMSContentForm()
    @Handler(operation='view', method='view')
    @Handler('my_contents')
    def SetOperations(self):pass


    def view(self, key, *args):
        cnt = cms.CMSContent.get(key)
        if cnt: return {'content':cnt}
        self.status = "Content Not Found"
        self.redirect('/cms/contents')


    @View(templateName = 'CMSContent.html')
    def index(self, *args):
        limit = 10
        offset = 0
        try:
            offset = int(self.params.offset)
        except:
            pass
        contents = cms.CMSContent.all().order('-DateCreated').fetch(limit=limit, offset=offset)
        return {'contents':contents}

    @LogInRequired()
    @View(templateName = "CMSContent.html")
    def my_contents(self):
        limit = self.params.limit or 20
        offset = self.params.offset or 0
        contents = cms.CMSContent.all().filter("Creator =", self.User).fetch(limit, offset)
        return {'contents':contents}

    @AdminOnly()
    @Post()
    def save(self, *args):
        form = CMSContentForm(data=self.params)
        if form.is_valid():
            data =form.clean()
            tags = []
            try:
                tags = [x.strip() for x in data['Tags'].split(',')]
            except:
                pass
            if not self.params.key:
                cms.CMSContent.CreateNew(title=data['Title'], content=data['Content'], tags=tags, creator=self.User, _isAutoInsert=True)
            else:
                content= cms.CMSContent.get(self.params.key)
                content.HTMLContent = data["Content"]
                extra_tags = [t for t in tags if t not in content.Tags]
                tags_to_remove = [t for t in content.Tags if t not in tags]
                content.Tags = tags
                content.put()
                for tag in extra_tags:
                    cms.ContentTag.IncrementTag(tag)
                for tag in tags_to_remove:
                    cms.ContentTag.DecrementTag(tag)

            #map(ContentTag.IncrementTag, tags)
            #cms.
            self.status ="Content is saved"
        else:
            self.status ='Content is Invalid'
            self.extra_context['op']=self.params.key and 'update' or 'insert'
            self.ContentForm = form
        self.redirect('/cms/links')

    def edit(self, key=None,*args):
        cmsContent =None
        if key:
            cmsContent = cms.CMSContent.get(key)
            self.ContentForm = CMSContentForm(initial={'Title':cmsContent.Title,
                                                       'Content':cmsContent.HTMLContent,
                                                       'Tags':','.join([str(x) for x in cmsContent.Tags])})


        self.extra_context['op']=key and 'update' or 'insert'
        return {'content':cmsContent, 'CMSContentForm':self.ContentForm}

    @ErrorSafe(redirectUrl='/cms/content')
    def delete(self, *args):
        result = True
        if self.params.key:
            cms.CMSContent.get(self.params.key).delete()
            self.status='CMS Content has been deleted!'
        else:
            result=False
            self.status='Key Not Provided'
        if self.isAjax:
            return str(result)
        else:
            self.redirect(self.get_url())

class CMSPageController(CMSBaseController):
    def __init__(self,*args, **kwargs):
        super(CMSPageController,self).__init__(*args, **kwargs)
    @ClearDefaults()
    @Default('index')
    @Handler('view', 'view')
    def SetOperations(self):pass

    def view(self, pagepath):
        lnk = cms.CMSLink.GetLinkByPath(pagepath)
        if lnk:
            return {'link':lnk}
        else:
            self.status ="Not Valid Page"
            self.redirect(LoginController.get_url())
    @View(templateName='CMSPage_index.html')
    def index(self, tag=None):

        limit = int(self.params.limit or 20)
        offset = int(self.params.offset or 0)
        if not tag:
            return {'links':cms.CMSLink.all().fetch(limit, offset)}
        else:
            contents=cms.CMSContent.gql("WHERE Tags =:t",t=tag).fetch(limit=limit, offset=offset)
            arr = [x.Links for x in contents]
            links = []
            for x in arr:
                links+=x
            links = db.get(list(set(links)))
            return {'links':links}

class CommentController(CMSBaseController):
    def __init__(self,*args, **kwargs):
        super(CommentController).__init__(*args, **kwargs)

    @Default('save')
    def SetOperations(self): pass

    def save(self, key):
        if self.params.Comment:
            Comment.CreateNew(self.params.Comment, self.User, cms.CMSContent.get(key), _isAutoInsert=True)
            self.status = 'Comment is saved'
        else:
            self.status = 'No Comment was given'
        if self.isAjax:
            simplejson.dumps({'status':self.status})
        else:
            self.redirect(CMSContentController.get_url(), permanent=True)

    def delete(self,*args):
        if self.params.key:
            item = Comment.get(self.params.key)
            if item:
                item.delete()
                self.status ='Comment is deleted!'
            else:
                self.status='Comment does not exist'
        else:
            self.status = 'Key was not Provided!'
        self.redirect(CommentController.get_url())

    def index(self, *args):
        results =None
        index = 0; count=20
        try:
            index = int(self.params.index)
            count = int(self.params.count)
        except:
            pass
        nextIndex = index+count;
        previousIndex = index<=0 and -1 or (index-count>0 and 0 or index-count)
        result = {'CommentList': Comment.all().fetch(limit=count, offset=index)}
        result.update(locals())
        return result

    def edit(self, *args):
        if self.params.key:
            item = Comment.get(self.params.key)
            if item:
                return {'op':'update', 'CommentForm': CommentForm(instance=item)}
            else:
                self.status = 'Comment does not exists'
                self.redirect(CommentController.get_url())
        else:
            self.status = 'Key not provided'
            return {'op':'insert' ,'CommentForm':CommentForm()}
