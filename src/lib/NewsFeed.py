from datetime import datetime
from Models.BaseModels import Person
import uuid
class FeedEntry(object):
    Title=''
    Link=''
    Guid=uuid.uuid4()
    TimeUpdated=datetime.now()
    Summary=''
    
class NewsFeed(object):
    Title =''
    Subtitle =''
    Description=''
    FeedUrl=''
    PageUrl=''
    Guid = uuid.uuid4()
    TimeUpdated= datetime.now()
    Author = None
    Entries = []
    def CreateEntry(self, title, link, guid, summary):
        res = FeedEntry(Title=title,
                  Link=link,
                  Guid=guid,
                  Summary=summary,
                  )
        self.Entries.append(res)
        return res