# -*- coding: utf-8 -*-
from google.appengine.ext.db.djangoforms import ModelForm
from google.appengine.ext import db
from google.appengine.ext.db import polymodel
import datetime as dt
###########

class Person(polymodel.PolyModel):
    '''A Person with UserName, Name, Surname Phone Email e.t.c'''
    UserName = db.StringProperty(required=True)
    Password = db.StringProperty(required=True)
    Name = db.StringProperty(required=False)
    Surname = db.StringProperty(required=False)
    Email = db.EmailProperty(required=False)
    Public = db.BooleanProperty(default=True)
    Notify = db.BooleanProperty(default=False)
    DateAdded = db.DateTimeProperty()
    PhotoUrl = db.LinkProperty()
    AuthenticationType = db.StringProperty(default='local')
    IsAdmin = db.BooleanProperty(default=False)
    def put(self):
        _isValid_, _error_ = self.__validate__()
        if(_isValid_):
            if not self.is_saved():
                self.DateAdded = dt.datetime.now()
            super(Person, self).put()
        else:
            raise Exception(_error_)

    def __validate__(self):
        __errors__ = []
        if not self.UserName or len(self.UserName)<3:
            __errors__.append('UserName must not be less than 3 characters')
        if not self.Email and self.AuthenticationType == 'local': #or self.Email.validate('^[0-9,a-z,A-Z,.]+@[0-9,a-z,A-Z].[com, net, org]'):
            __errors__.append('Email Must Not be Empty')
        if len(self.Password) < 6  or str(self.Password).find(self.Name) >= 0:
            __errors__.append('Not a good Password(Must be at least 6 characters long, and not containing your name')

        return not __errors__ and (True, None) or (False, ' and\r\n'.join(__errors__))

    @classmethod
    def CreateNew(cls, uname, name, surname, email, password, public=True, notify=True, authType=None, photoUrl=None, _autoSave=False):
        result = cls(UserName = uname,
                    Email=email,
                    Name=name,
                    Surname=surname,
                    Password=password,
                    Public=public,
                    Notify=notify,
                    PhotoUrl=photoUrl
                    )
        if authType: result.AuthenticationType = authType
        
        if _autoSave:
            result.put()
        return result
    @classmethod
    def GetUser(cls, uname, password, authType):
        u = None
        if '@' in uname:
            u = cls.gql('WHERE Password= :passwd AND Email= :uname AND AuthenticationType= :auth', uname=uname, passwd=password, auth=authType).get()
        else:
            u = cls.gql('WHERE Password= :passwd AND UserName= :uname AND AuthenticationType= :auth', uname=uname, passwd=password, auth=authType).get()
        return u
    def __str__(self):
        return self.Name+' '+self.Surname
class PersonForm(ModelForm):
    class Meta():
        model = Person
## End Person
##**************************

class WishList(db.Model):
    '''Whishes for the page look&feel and functionality '''
    Owner = db.ReferenceProperty(Person)
    Wish  = db.TextProperty()
    DateAdded = db.DateTimeProperty(auto_now_add=True)
    @classmethod
    def CreateNew(cls, owner, wish, _isAutoInsert=False):
        result = cls(Owner=owner, Wish=wish, DateAdded = dt.datetime.now())
        if _isAutoInsert: result.put()
        return result
    
    @classmethod
    def GetAll(cls, limit=1000, offset=0):
        return cls.all().fetch(limit=limit, offset=offset)
    
    def __str__(self):
        return self.Wish+'-'+self.Owner.__str__()
class WishListForm(ModelForm):
#    DateAdded = fields.DateField(widget=widgets.TextInput(attrs={'class':'date'}))
    class Meta():
        model=WishList
        exclude = ['Owner']
## End WishList
##**************************

class Role(db.Model):
    """TODO: Describe Role"""
    RoleName= db.StringProperty(required=True, )
    RoleDescription= db.TextProperty(required=True, )
    
    @classmethod
    def CreateNew(cls ,rolename,roledescription , _isAutoInsert=False):
        result = cls(
                     RoleName=rolename,
                     RoleDescription=roledescription,)
        if _isAutoInsert: result.put()
        return result
    def __str__(self):
        return self.RoleName 
class RoleForm(ModelForm):
    class Meta():
        model=Role
## End Role
##**************************

class RoleAssociation(db.Model):
    """Association Class between Users and Roles"""
    Role= db.ReferenceProperty(Role, collection_name='role_roleassociations', )
    Person= db.ReferenceProperty(Person, collection_name='person_roleassociations', )

    @classmethod
    def CreateNew(cls ,rolename,roledescription,role,person , _isAutoInsert=False):
        result = cls(Role=role,
                     Person=person,)

        if _isAutoInsert: result.put()
        return result
    def __str__(self):
        return self.Role.RoleName #+'-'+self.Person and self.Person.Name or 'None'+' '+self.Person and self.Person.Surname or 'None'
class RoleAssociationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(RoleAssociationForm, self).__init__(*args, **kwargs)
        self.fields['Person'].queryset = Person.all().fetch(limit=100)
    class Meta():
        model=RoleAssociation
## End RoleAssociation
##**************************

class Invitation(db.Model):
    """Creates new invitation for user to register on the web site
    Initialy a user is created. so after the user registers only it's information will be updated
    when the user registers the Accepted property is set to true"""
    InviteFrom= db.ReferenceProperty(Person, collection_name='invitefrom_invitations', required=True, )
    InvitationDate= db.DateProperty(auto_now_add=True, )
    PersonBinding= db.ReferenceProperty(Person, collection_name='personbinding_invitations', required=True, )
    Accepted= db.BooleanProperty(default=False, )
    DateAccepted = db.DateProperty()
    @classmethod
    def CreateNew(cls ,invitefrom, personbinding, _isAutoInsert=False):
        result = cls(InviteFrom=invitefrom,PersonBinding=personbinding,)
        if _isAutoInsert: result.put()
        return result
    def accept(self):
        self.Accepted = True
        self.DateAccepted = dt.datetime.now()
        self.put()
    def __str__(self):
        return '('+(self.Accepted and 'Y' or 'N')+')From '+self.InviteFrom.UserName+' to '+self.PersonBinding.UserName+' on '+str(self.InvitationDate)
## End Invitation
