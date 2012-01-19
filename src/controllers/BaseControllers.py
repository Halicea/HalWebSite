from google.appengine.api import urlfetch
from django.utils import simplejson
import urllib, os
from forms.BaseForms import InvitationForm, RegisterForm
#{%block imports%}
from lib.halicea.HalRequestHandler import HalRequestHandler as hrh
from lib.halicea.decorators import *
from models.BaseModels import RoleAssociation, RoleAssociationForm 
from models.BaseModels import Role, RoleForm 
from models.BaseModels import Person
from models.BaseModels import Invitation
from models.BaseModels import WishList, WishListForm
from forms.BaseForms import LoginForm
#{%endblock%}

class LoginController( hrh ):
    @Default('login')
    @Handler('logout')
    @Handler('JanrainAuth','JanrainAuth')
    @Handler('register')
    def SetOperations(self):pass

    @View(templateName='Login.html')
    def login(self, *args):
        if self.method=='GET':
            return self.login_get(*args)
        else:
            return self.login_post(*args)
    @ErrorSafe()
    def JanrainAuth(self, *args):
        token = self.params.token
        url = 'https://rpxnow.com/api/v2/auth_info'
        args = {
          'format': 'json',
          'apiKey': '4a593fc2715670ab6a03b40653054858ffdc34a2',
          'token': token
          }
        r = urlfetch.fetch(url=url,
                           payload=urllib.urlencode(args),
                           method=urlfetch.POST,
                           headers={'Content-Type':'application/x-www-form-urlencoded'}
                           )
    
        json = simplejson.loads(r.content)
    
        if json['stat'] == 'ok':
            person = Person.gql("WHERE UserName= :u AND AuthenticationType= :auth", u=json['profile']['preferredUsername'], auth=json['profile']['providerName']).get()
            if not person:
                name = json['profile'].has_key('givenName') and json['profile']['givenName'] or ''
                surname = json['profile'].has_key('familyName') and json['profile']['name']['familyName'] or ''
                display  = json['profile'].has_key('displayName') and json['profile']['displayName'] or ''
                email  = json['profile'].has_key('email') and json['profile']['email'] or None
                photo = json['profile'].has_key('photo') and json['profile']['photo'] or None
                if not name and not surname and display:
                    arr = display.split(' ')
                    name = arr[0]; 
                    surname = len(arr)>1 and arr[1] or ''
                if len(args)==1:
                    person = Person.get(args[0])
                    person.UserName=json['profile']['preferredUsername'],
                    person.Name=name,
                    person.Surname=surname,
                    person.Email = email,
                    person.Password='openid',
                    person.Public=True,
                    person.Notify=True,
                    person.AuthenticationType=json['profile']['providerName'],
                    person.PhotoUrl=photo,
                    person.put()
                else:
                    person = Person.CreateNew(uname=json['profile']['preferredUsername'],
                                              name=name,
                                              surname=surname,
                                              email = email,
                                              password='openid',
                                              public=True,
                                              notify=True,
                                              authType=json['profile']['providerName'],
                                              photoUrl=photo,
                                              _autoSave=True)
                    
            self.login_user(person)
            self.status = 'Welcome '+person.UserName
            if self.params.redirect_url:
                self.redirect(self.params.redirect_url)
            else:
                self.redirect('/')
        else:
            self.status = 'Not Valid Login'
            self.respond()

    def login_post(self , *args):
        lform  = LoginForm(formdata = self.request.params)
        if lform.validate():
            if(self.login_user_local(lform.data['Email'], lform.data['Password'])):
                if lform.data['RedirectUrl']:
                    self.redirect( lform.data['RedirectUrl'])
                else:
                    self.redirect( '/' )
                return
            else:
                self.status = "Username or Password are Not Correct"
                lform['Password']=""
                return {'LoginForm':lform}
        else:
            return {'LoginForm':lform}

    def login_get( self, *args ):
        if not self.User:
            if self.g('redirect_url'):
                return {'LoginForm':LoginForm(initial={'RedirectUrl':self.params.redirect_url})}
            else:
                return {'LoginForm':LoginForm()}
        else:
            self.redirect( '/' )

    def logout(self):
        self.logout_user()
        self.redirect( LoginController.get_url() )
    
    def register_view(self, form=None):
        return {'register':form or RegisterForm()}

    def register(self):
        reg = RegisterForm()
        if self.method == 'POST':
            self.SetTemplate(templateName='thanks.html')
            reg = RegisterForm(self.request.POST)
            if reg.validate():                
                user = Person.CreateNew(
                                reg.data['UserName'], 
                                reg.data['Name'], 
                                reg.data['Surname'], 
                                reg.data['Email'],                                     
                                reg.data['Password'],
                                reg.data['Public'],
                                reg.data['Notify'],
                                'local', 
                                None, 
                                _autoSave=True)
                return {'uname':' '.join([user.Name, user.Surname])}  
        self.SetTemplate(templateName='register.html')
        return {'register':reg}

class RoleController(hrh):
    def edit(self):
        self.SetTemplate(templateName='Role_shw.html')
        if self.params.key:
            item = Role.get(self.params.key)
            if item:
                return {'op':'upd', 'RoleForm': RoleForm(instance=item)}
            else:
                self.status = 'Role does not exists'
                self.redirect(RoleController.get_url())
        else:
            self.status = 'Key not provided'
            return {'op':'ins' ,'RoleForm':RoleForm()}
    def delete(self):
        if self.params.key:
            item = Role.get(self.params.key)
            if item:
                item.delete()
                self.status ='Role is deleted!'
            else:
                self.status='Role does not exist'
        else:
            self.status = 'Key was not Provided!'
        self.redirect(RoleController.get_url())
    def index(self):
        self.SetTemplate(templateName='Role_lst.html')
        results =None
        index = 0; count=1000
        try:
            index = int(self.params.index)
            count = int(self.params.count)
        except:
            pass
        result = {'RoleList': Role.all().fetch(limit=count, offset=index)}
        result.update(locals())
        self.respond(result)
    def save(self):
        instance = None
        if self.params.key:
            instance = Role.get(self.params.key)
        form=RoleForm(data=self.request.POST, instance=instance)
        if form.is_valid():
            result=form.save(commit=False)
            result.put()
            self.status = 'Role is saved'
            self.redirect(RoleController.get_url())
        else:
            self.SetTemplate(templateName = 'Role_shw.html')
            self.status = 'Form is not Valid'
            result = {'op':'upd', 'RoleForm': form}
            self.respond(result)

class RoleAssociationController(hrh):
    def edit(self, *args):   
        self.SetTemplate(templateName='RoleAssociation_shw.html')
        if self.params.key:
            item = RoleAssociation.get(self.params.key)
            if item:
                result = {'op':'upd', 'RoleAssociationForm': RoleAssociationForm(instance=item)}
                self.respond(result)
            else:
                self.status = 'RoleAssociation does not exists'
                self.redirect(RoleAssociationController.get_url())
        else:
            self.status = 'Key not provided'
            self.respond({'op':'ins' ,'RoleAssociationForm':RoleAssociationForm()})
    def delete(self, *args):
        if self.params.key:
            item = RoleAssociation.get(self.params.key)
            if item:
                item.delete()
                self.status ='RoleAssociation is deleted!'
            else:
                self.status='RoleAssociation does not exist'
        else:
            self.status = 'Key was not Provided!'
        self.redirect(RoleAssociationController.get_url())
    def index(self, *args):
        self.SetTemplate(templateName='RoleAssociation_lst.html')
        results =None
        index = 0; count=1000
        try:
            index = int(self.params.index)
            count = int(self.params.count)
        except:
            pass
        result = {'RoleAssociationList': RoleAssociation.all().fetch(limit=count, offset=index)}
        result.update(locals())
        self.respond(result)
    def save(self, *args):
        instance = None
        if self.params.key:
            instance = RoleAssociation.get(self.params.key)
        form=RoleAssociationForm(data=self.request.POST, instance=instance)
        if form.is_valid():
            result=form.save(commit=False)
            result.put()
            self.status = 'RoleAssociation is saved'
            self.redirect(RoleAssociationController.get_url())
        else:
            self.SetTemplate(templateName = 'RoleAssociation_shw.html')
            self.status = 'Form is not Valid'
            result = {'op':'upd', 'RoleAssociationForm': form}
            self.respond(result)

class WishListController(hrh):
    def index(self):
        self.SetTemplate(templateName='WishList_lst.html')
        results =None
        index = 0; count=1000
        try:
            index = int(self.params.index)
            count = int(self.params.count)
        except:
            pass
        result = {'WishListList': WishList.all().fetch(limit=count, offset=index)}
        result.update(locals())
        self.respond(result)
    def edit(self):
        self.SetTemplate(templateName='WishList_shw.html')
        if self.params.key:
            item = WishList.get(self.params.key)
            if item:
                result = {'op':'upd', 'WishListForm': WishListForm(instance=item)}
                self.respond(result)
            else:
                self.status = 'WishList does not exists'
                self.redirect(WishListController.get_url())
        else:
            if self.method == 'POST':
                self.status = 'Key not provided'
            self.respond({'op':'ins' ,'WishListForm':WishListForm()})
    def save(self):
        form = None
        if self.params.key:
            instance = WishList.get(self.params.key)
            form = WishListForm(instance=instance) 
        else:
            form = WishListForm(data=self.request.POST)
        if form.is_valid():
            result=form.save(commit=False)
            result.Owner = self.User
            result.put()
            self.status = 'WishList is saved'
            self.redirect(WishListController.get_url())
        else:
            self.SetTemplate(templateName = 'WishList_shw.html')
            self.status = 'Form is not Valid'
            result = {'op':'upd', 'WishListForm': form}
            self.respond(result)
    def delete(self):
        if self.params.key:
            item = WishList.get(self.params.key)
            if item:
                item.delete()
                self.status ='WishList is deleted!'
            else:
                self.status='WishList does not exist'
        else:
            self.status = 'Key was not Provided!'
        self.redirect(WishListController.get_url())

class InvitationController(hrh):

    @ClearDefaults()
    @Default('create')
    @Handler('create', 'create')
    @Handler('index', 'index')
    @Handler('delete', 'delete')
    def SetOperations(self):pass

    @Post()
    @ErrorSafe()
    @ResponseType('json')
    def create(self,*args):
        form = InvitationForm(data=self.request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            from google.appengine.api import mail
            p=Person.CreateNew(uname=email, email=email,
                             name=email,surname=email,
                             password='blablabla', _autoSave=True)
            
            inv =Invitation.CreateNew(invitefrom=self.User, personbinding=p, _isAutoInsert=True)
            mail.send_mail(sender='admin@halicea.com',to=p.Email,subject='Invitation for Bordj',
                           body="""Dear Mr/Ms,<br/>
    You have been invited to register on Bordj app from {%s}.<br/>
    Please go to this <a href="%s">link</a> in order to finish the registration.<br/>
    <b>Note:</b>Registration info will expire in 7 days.<br/>
    Regards,
       Bordj Admin"""%(self.User, LoginController.get_url(inv.key().__str__())))
            return """{result:True, message:"Invitation is sent to the user"}"""

    def index(self, accepted=False, *args):
        results =None
        index = 0; count=20
        try:
            index = int(self.params.index)
            count = int(self.params.count)
        except:
            pass
        nextIndex = index+count;
        previousIndex = index<=0 and -1 or (index-count>0 and 0 or index-count) 
        result = {'InvitationList': Invitation.all().filter('Accepted = ', accepted).fetch(limit=count, offset=index)}
        result.update(locals())
        return result
    @ResponseType('json')
    def delete(self, *args):
        Invitation.get(self.params.key).delete()
        return {'message':'Item is deleted'}

