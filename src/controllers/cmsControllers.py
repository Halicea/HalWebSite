import yaml
from lib.halicea.decorators import *
import models.cmsModels as cms
from controllers.BaseControllers import LoginController
from lib.halicea.HalRequestHandler import HalRequestHandler as hrh
from forms.cmsForms import CMSContentForm, CMSMenuForm
from google.appengine.ext import db
from lib import messages
from django.utils import simplejson
from models import cmsModels

contentTypeViews={cmsModels.ContentType.CMSPage:'CMSPage.html',
                  cmsModels.ContentType.CMSPage:'CMSPost.html',
                  }

class CMSBaseController(hrh):
    def __init__(self, *args, **kwargs):
        super(CMSBaseController, self).__init__(*args, **kwargs)
        self.extra_context={'tags':cms.ContentTag.all().order('-Count').fetch(10, 0)}

class CMSLinksController(CMSBaseController):
    def __init__(self, *args, **kwargs):
        super(CMSLinksController, self).__init__(*args, **kwargs)
    @ClearDefaults()
    @Default('index')
    @Handler('save')
    @Handler('delete')
    def SetOperations(self):pass
    @AdminOnly()
    
    @View(templateName='CMSLinks.html')
    def index(self, menu='cms', *args):
        result ={'CMSContentForm': CMSContentForm(), 'MenuForm':CMSMenuForm(), };
        result.update(self.plugins.Contents.index())
        result.update(self.plugins.Menus.index())
        return result

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
            cms.CMSLink.CreateNew(addressName, name, parent, order, content, contentType, creator, _isAutoInsert=True)
        if self.isAjax:
            return self.plugins.Menus.view(self.params.menu)
        else:
            return self.index()
    
    @AdminOnly()
    def delete(self, *args):
        lnk=cms.CMSLink.get(self.params.key)
        if lnk:
            if lnk.Content and lnk.Content.content_cms_links.count()==1:
                lnk.Content.delete()
            menus = lnk.linkroot_menus.fetch(10)
            if menus:
                for menu in menus: CachedResource.clear(MenuController.view, menu.Name)
                db.delete(menus)
            lnk.delete()
            self.status='Link is deleted'
        else:
            self.status="Link is invalid";
        return self.isAjax and self.status or self.redirect(self.get_url())
class MenuController(CMSBaseController):
    
    def __init__(self, *args, **kwargs):
        super(MenuController, self).__init__(*args, **kwargs)
        self.base = '/cms'
    
    @ClearDefaults()
    @Default('view')
    @Handler('edit')
    @Handler(operation='new', method='edit')
    @Handler('save')
    @Handler('index')
    @Handler('index_combo')
    @Handler('delete')
    def SetOperations(self):pass
    
    #@CachedResource()
    def view(self, menu='cms'): 
        result=  cms.Menu.get_by_key_name(menu)
        if result:
            return self.__view_list__(result, self.params)
        else:
            return "No Menu Found"
    
    def __view_list__(self, menu=None, params=None):  
        id, name, cl, style = str(menu.key()), menu.Name, '', ''
        noroot = False
        if params:
            name, cl, style = params.name or menu.Name, params.cl or cl, params.style or style 
            noroot = False or params.noroot
        template= "<ul id='menu_%(name)s' name='menu_%(name)s' class='%(class)s' style='%(style)s'>\n\t<li><a href='#' id='%(key)s'>Root</a><ul>%(rest)s<ul></li>\n</ul>"
        result = "" 
        for k in menu.LinkRoot.parent_link_cms_links.fetch(10):
            result+=self.__renderNode__(k, 2)
        if noroot:
            return result
        else:
            return template%{'id':id, 'name':name, 'style':style, 'class':cl,'key':str(menu.LinkRoot.key()),'rest':result}
    
    def __renderNode__(self, node, spacer, circ_ref_stop=[]):
        self.base
        link = '\n'+('\t'*spacer)+"<li><a href='%(base)s/%(url)s' id='%(key)s'>%(name)s</a><ul>%(rest)s</ul></li>"
        nodes_to_continue = [x for x in node.parent_link_cms_links if x.key().__str__() not in circ_ref_stop]
        circ_ref_stop.extend([x.key().__str__() for x in nodes_to_continue])
        return link%{'base':self.base, 'url':node.Url(), 'key':str(node.key()), 'name':node.Name, 'rest':'\n'.join([self.__renderNode__(x, spacer+1, circ_ref_stop) for x in nodes_to_continue])}

    @CachedResource()
    def index(self,*args):
        return {'menus':cms.Menu.all()}
    
    def index_combo(self,*args):
        combo_template ="<option value='{0}'>{0}</option>"
        li_template = "<li></li>"
        return "<option value='no_menu'>--Select Item--</option>"+'\r\n'.join([combo_template.replace("{0}",(x.Name)) for x in cms.Menu.all()])

    def delete(self, key):
        menu = cms.Menu.get(key)
        CachedResource.clear(MenuController.index)
        CachedResource.clear(MenuController.index_combo)
        CachedResource.clear(MenuController.view, menu.Name)
        menu.delete()
    
    @View(templateName='Menu_edit.html')
    def edit(self,*args):
        menu = None
        frm = None
        if self.params.key:
            menu = cms.Menu.get(self.params.key)
            frm =CMSMenuForm(initial={'key':menu.key().__str__(), 'Name':menu.Name, 'Description':menu.Description}) 
        else: frm = CMSMenuForm()
        return {'MenuForm':frm}
    
    @Post()
    @View(templateName='Menu_edit.html')
    @ClearCacheAfter(CMSLinksController.index, lambda r, *args, **kwargs: ([],{}) )
    def save(self, *args):
        frm = CMSMenuForm(self.params)
        if frm.is_valid():
            data = frm.clean()
            menu = cms.Menu.CreateNew(name=data["Name"], locationId="none", cssClass=None, creator=self.User, _isAutoInsert= True)
            if data['key']:
                menu = cms.Menu.get(data['key'])
                CachedResource.clear(MenuController.view, menu.Name)
            menu.Name =  data["Name"]
            menu.put()
            CachedResource.clear(MenuController.index)
            CachedResource.clear(MenuController.index_combo)
            self.message ='Menu was saved'
            return None
        else:
            return {'MenuForm':frm}

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
        if self.isAjax:
            return '\r\n'.join(['<option value="%s">%s</option>'%(str(c.key()),c.Title) for c in contents])
        else:
            return {'contents':contents}

    def index_li(self, *args):
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
        if self.isAjax:
            self.SetTemplate(templateGroup="form", templateName="CMSContentForm_edit.html")
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
    @Handler('view')
    def SetOperations(self):pass
    
    def view(self, url):
        lnk = cms.CMSLink.GetLinkByPath(url)
        if lnk:
            self.SetTemplate(templateName=contentTypeViews[lnk.ContentTypeNumber])
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
