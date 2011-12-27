from lib.gaesessions import get_current_session
from models.BaseModels import Person

class Authentication(object):
    
    def __init__(self, *args, **kwargs):
        pass
    def __getSession__(self):
        return get_current_session()
    session = property(__getSession__)
    def GetUser(self):
        if self.session and self.session.is_active():
            return self.session.get('user', default=None)
        else:
            return None

    @property
    def User(self):
        return self.GetUser()
    def login_user_local(self, uname, passwd):
        self.logout_user()
        user = Person.GetUser(uname, passwd, 'local')
        if user:
            self.session['user']= user; return True            
        else:
            return False
    def login_user2(self, user):
        if user:
            self.session['user']= user
            return True            
        else:
            return False
    def logout_user(self): 
        if self.session.is_active():
            self.session.terminate()
        return True

class AjaxForm(object):
    __isAjax = False
    def initialize(request, response):
        pass
        
    def beginForm(self, action,name, method, successCallback="", failCallback=""):
        result = """
        <form id='%(name)s' action='%(action)s' method='%(method)s'>
        return result%"""
        
    def endForm(self, 'name'):
        </form>
        <script type='text/javascript'>
            %(jqstart)s
                $('#%(name)s').ajaxForm({
                 success:%(success)s,
                 error:%(error)s
                });
            %(jqend)s
        </script>
        """
        