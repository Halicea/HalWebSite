from google.appengine.ext import db
from BaseModels import Person
import datetime as dt
from lib.halicea.decorators import property

class CMSContent(db.Model):
    Title = db.StringProperty(required=True)
    HTMLContent = db.TextProperty(required=True)
    Tags = db.ListProperty(str, default=[])
    Creator = db.ReferenceProperty(Person, collection_name='creator_cms_pages')
    DateCreated = db.DateTimeProperty(auto_now_add=True)
    LastDateModified = db.DateTimeProperty(auto_now=True)
    Links = db.ListProperty(db.Key, default=[])
    HasLinks = db.BooleanProperty(default=False)
    @classmethod
    def CreateNew(cls, title, content, tags, creator, _isAutoInsert=False):
        result = cls(
                    Title=title,
                    HTMLContent=content,
                    Tags=tags,
                    Creator=creator,
                   )
        if _isAutoInsert:
            result.put()
        return result
    def delete(self, **kwargs):
        map(ContentTag.DecrementTag, self.Tags)
        db.Model.delete(self, **kwargs)
    def put(self, **kwargs):
        if not self.is_saved():
            map(ContentTag.IncrementTag, self.Tags)
        result=  db.Model.put(self, **kwargs)
        return result
    def get_links(self):
        if self.Links:
            return db.get(self.Links)
        return None

class ContentType:
    """
        CMSPage , part of the cms system, it usualy should be a part of some menu structure.
        External Page, can't have any children
        Static page is a regular page inside of the application
    """
    CMSPage = 0
    StaticPage = 1
    NoContent = 2
    Post = 3

class CMSLink(db.Model):
    """Link have parent link, have contant and come with several variations depending on the content type:
        1. CMSPage
        2. Static Page
        3. No Content (usualy just a parent link to some other links with content, sittuable for creating menus)
    """
    AddressName = db.StringProperty(required=True)
    AdditionalUrl = db.StringProperty()
    Name = db.StringProperty(required=True)
    ParentLink = db.SelfReferenceProperty(collection_name='parent_link_cms_links')
    Depth = db.IntegerProperty(required=True, default=-1)
    Order = db.IntegerProperty(required=True, default=100)
    Content = db.ReferenceProperty(required=False, default=None, reference_class=CMSContent, collection_name='content_cms_links')
    Creator = db.ReferenceProperty(Person, collection_name='creator_cms_links')
    ContentTypeNumber = db.IntegerProperty(default = 0)
    DateCreated =db.DateTimeProperty(auto_now_add=True)
    LastDateModified =db.DateTimeProperty(auto_now=True)
    
    def __str__(self):
        return self.ParentLink or "None"+"/"+self.AddressName
    
    def GetChildren(self):
        return CMSLink.gql("WHERE Depth =:depth AND ParentLink =:pl", depth=self.Depth+1, pl=self).fetch(limit=1000)

    def Url(self):
        if self.ContentTypeNumber == ContentType.CMSPage:
            result=self.AddressName
            cur_ln = self.ParentLink
            while cur_ln:
                #we can skip some url parts by setting some link with No address but this is not safe
                if cur_ln.AddressName:
                    result = cur_ln.AddressName+'/'+result
                cur_ln = cur_ln.ParentLink
            return result
        else:
            return self.AdditionalUrl
        
    def GetTreeBelow(self, ignoreAddresses=[]):
        children = self.GetChildren()
        result = {}
        for child in children :
            if not (child.AddressName in ignoreAddresses):
                ignoreAddresses.append(child.AddressName)
                result[child] = child.GetTreeBelow(ignoreAddresses)
        return result
    def delete(self):
        if self.Content:
            self.Content.Links.remove(self.key())
            self.Content.HasLinks = len(self.Content.Links)>0
            self.Content.put()
        #delete all the menus dependent on this links
        menus = self.linkroot_menus.fetch(10)
        if menus:
            db.delete(menus)
        super(CMSLink,self).delete()
        return "Link Deleted"
    def put(self):
        super(CMSLink, self).put()
        if self.Content:
            self.Content.Links.append(self.key())
            self.Content.HasLinks=True
            self.Content.put()

    ###############################
    ## Static Methods 
    @classmethod
    def GetLinkByPath(cls, path):
        items = [p for p in path.split('/') if p]
        curPar=None
        if items:
            curPar = CMSLink.get_by_key_name(items[0])
        if len(items)>1:
            i=1
            for lnkStr in items:
                new_item = CMSLink.gql("WHERE Depth =:depth AND ParentLink =:pl AND AddressName =:address",depth=i, pl=curPar, address=lnkStr).get()
                if new_item: 
                    curPar = new_item
                else:
                    curPar = None
                    break;
                i+=1;
        return curPar
    @staticmethod
    def GetLinksByDate(dateFrom, dateTo):
        return CMSLink.gql("WHERE LastDateModified > :ldf AND LastDateModified < :ldt ORDER BY LastDateModified ASC", ldf=dateFrom, ldt=dateTo).fetch(1000)
    
    @classmethod
    def CreateNew(cls, addressName, name, parentLink, order, content, contentType, creator, _isAutoInsert=False):
        if not parentLink:
            depth = -1
        else:
            depth = parentLink.Depth+1
        additionalUrl = None
        if contentType == ContentType.StaticPage:
            additionalUrl = addressName
            addressName = name
        if contentType==ContentType.NoContent:
            additionalUrl = ""
        result = cls(parent=parentLink, key_name=addressName, AddressName=addressName, 
                     AdditionalUrl=additionalUrl, Name=name, ContentTypeNumber=contentType, 
                     ParentLink=parentLink, Depth=depth, Order=order, 
                     Content=content, Creator=creator)
        if _isAutoInsert: result.put()
        return result
    
    @classmethod
    def GetLinkTree(cls, menu='cms'):
        root = CMSLink.get_by_key_name(menu)
        if not root:
            root = CMSLink.CreateNew2('/cms', 'Root', None, -1, None, None, _isAutoInsert=False)
        return root.GetTreeBelow({})
#        tree = cls.gql('WHERE Depth =:d', d=-1).fetch(limit=1000, offset=0)
#        result = {} 
#        # get the root nodes
#        for t in tree:
#            result[t] = t.GetTreeBelow()
#        return result
    ## End Static Methods
    
class Menu(db.Model):
    """Three of CMS Links"""
    Name = db.StringProperty(required = True)
    LocationId = db.TextProperty(required = True)
    CssClass = db.StringProperty()
    LinkRoot = db.ReferenceProperty(CMSLink, collection_name='linkroot_menus')
    @classmethod
    def CreateNew(cls, name, locationId, cssClass, creator, _isAutoInsert=False):
        root = CMSLink.CreateNew(name, name,  None, -1, None, ContentType.NoContent, creator, _isAutoInsert=_isAutoInsert)
        res = cls(key_name=name, Name=name, LocationId=locationId, CssClass = cssClass, LinkRoot=root)
        if _isAutoInsert: res.put()
        return res
    @classmethod
    def CreateFromLinkRoot(cls, name, locationId, cssClass, linkRoot,_isAutoInsert=False):
        res = cls(key_name=name, Name=name, LocationId=locationId, CssClass = cssClass, LinkRoot=linkRoot)
        if _isAutoInsert: res.put()
        return res
    def put(self):
        self.LinkRoot.put()
        super(Menu, self).put()
    def delete(self):
        self.LinkRoot.delete()
        super(Menu, self).delete()
    def to_list(self, params=None):
        id, name, cl, style = str(self.key()), self.Name, '', ''
        noroot = False
        if params:
            name, cl, style = params.name or self.Name, params.cl or cl, params.style or style 
            noroot = False or params.noroot
        template= "<ul id='menu_%(name)s' name='menu_%(name)s' class='%(class)s' style='%(style)s'>\n\t<li><a href='#' id='%(key)s'>Root</a><ul>%(rest)s<ul></li>\n</ul>"
        result = "" 
        for k in self.LinkRoot.parent_link_cms_links.fetch(10):
            result+=self.__renderNode__(k, 2)
        if noroot:
            return result
        else:
            return template%{'id':id, 'name':name, 'style':style, 'class':cl,'key':str(self.LinkRoot.key()),'rest':result}
    
    def __renderNode__(self, node, spacer, circ_ref_stop=[]):
        link = '\n'+('\t'*spacer)+"<li><a href='%(url)s' id='%(key)s'>%(name)s</a><ul>%(rest)s</ul></li>"
        nodes_to_continue = [x for x in node.parent_link_cms_links if x.key().__str__() not in circ_ref_stop]
        circ_ref_stop.extend([x.key().__str__() for x in nodes_to_continue])
        return link%{'url':node.Url(), 'key':str(node.key()), 'name':node.Name, 'rest':'\n'.join([self.__renderNode__(x, spacer+1, circ_ref_stop) for x in nodes_to_continue])}
    
    def __str__(self):
        return self.Name
    
class ContentTag(db.Model):
    """Tags for some Content"""
    TagName = db.StringProperty(required=True)
    Count = db.IntegerProperty(default=0)
    @staticmethod
    def IncrementTag(tagName):
        tag = ContentTag.get_or_insert(tagName, TagName=tagName)
        tag.Count+=1
        tag.put()
    @staticmethod
    def DecrementTag(tagName):
        tag = ContentTag.get(tagName)
        if tag:
            if tag.Count==1:
                tag.delete()
            else:
                tag.Count-=1
                tag.put()
            