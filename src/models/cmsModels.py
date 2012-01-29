from google.appengine.ext import db
from BaseModels import Person
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
    BlogPost=4
    
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
        return self.Url()
    
    def GetChildren(self):
        return CMSLink.gql("WHERE Depth =:depth AND ParentLink =:pl", depth=self.Depth+1, pl=self).fetch(limit=1000)

    def Url(self):
        if self.ContentTypeNumber not in [ContentType.StaticPage, ContentType.NoContent]:
            result=self.AddressName
            cur_ln = self.ParentLink
            while cur_ln:
                #we can skip some url parts by setting some link with No address but this is not safe
                if cur_ln.AddressName:
                    result = cur_ln.AddressName+'/'+result
                cur_ln = cur_ln.ParentLink
            return result
        elif self.ContentTypeNumber == ContentType.NoContent:
            return "#"
        elif self.ContentTypeNumber == ContentType.StaticPage:
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
            curPar = Menu.get_by_key_name(items[0]).LinkRoot
        if len(items)>1:
            i=1
            for lnkStr in items[1:]:
                new_item = CMSLink.gql("WHERE ParentLink =:pl AND AddressName =:address", pl=curPar, address=lnkStr).get()
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
        elif contentType==ContentType.NoContent:
            additionalUrl = ""
        
        result = cls(parent=parentLink, AddressName=addressName, 
                     AdditionalUrl=additionalUrl, Name=name, ContentTypeNumber=contentType, 
                     ParentLink=parentLink, Depth=depth, Order=order, 
                     Content=content, Creator=creator)
        if _isAutoInsert: result.put()
        return result
    
    @classmethod
    def GetLinkTree(cls, menu='cms'):
        root = CMSLink.get_by_key_name(menu)
        return root.GetTreeBelow({})
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
            