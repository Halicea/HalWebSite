from lib.wtforms import * 
from lib.wtforms.ext.appengine.db import model_form
#{%block imports%}
from models.BaseModels import *
#{%endblock%}

PersonForm = model_form(Person) 
RoleForm = model_form(Role)
class LoginForm(form.Form):
  RedirectUrl = fields.HiddenField()
  Email = fields.TextField(validators=[validators.required(), validators.length(5, 30)])
  Password = fields.PasswordField(validators=[validators.required()])


class RegisterForm(form.Form):
  UserName = fields.TextField(validators=[validators.required(),validators.length(5, 30)]) 
  Name = fields.TextField(validators=[validators.required(),validators.length(2, 30)]) 
  Surname=fields.TextField(validators=[validators.required(),validators.length(2, 30)]) 
  Email = fields.TextField(validators=[validators.required(),validators.email()]) 
  Password = fields.PasswordField(validators=[validators.required(),validators.length(5, 30)]) 
  Public=fields.BooleanField(default=True) 
  Notify = fields.BooleanField(default=True)
  

class InvitationForm(Form):
  Email = fields.TextField(validators=[validators.email(), validators.required()])