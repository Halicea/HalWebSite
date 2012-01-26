from lib.wtforms import *
#{%block imports%}
from models.cmsModels import *
#{%endblock%}

class CMSContentForm(form.Form):
  Title = fields.TextField(validators = [validators.required("Title is Required"),])
  Content = fields.TextField(validators = [validators.required("Title is Required"),])
  Tags = fields.TextField()

class CMSMenuForm(form.Form):
  key = fields.HiddenField()
  Name = fields.TextField(validators=[validators.required(), validators.length(3, -1)])
