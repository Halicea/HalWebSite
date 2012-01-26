from lib.gaesessions import get_current_session
from models.BaseModels import Person
from lib.halicea.helpers import DynamicParameters, LazyDict
class AuthenticationMixin(object):
  Impersonated=None
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
    if self.Impersonated:
      return self.Impersonated
    else:
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
  def initialize(self, *args, **kwargs):
    pass
  def beginForm(self, name="", action="",  method="", successCallback="", failCallback=""):
    result = """<script type='text/javascript'>
  $(function(){
    $('#%(name)s').ajaxForm({
     success:%(success)s,
     error:%(error)s
    });
  });
</script>
<form id='%(name)s' action='%(action)s' method='%(method)s'>
return result%"""
    return result

  def endForm(self, name):
    result="""</form>
    """

class HtmlMixin(object):
  def __init__(self, *args, **kwargs):
    self.Html = DynamicParameters(LazyDict({
                'AjaxForm':AjaxForm,
                }, 'initialize'))